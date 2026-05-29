from __future__ import annotations

import argparse
import json
import mimetypes
import pathlib
import sys
import urllib.error
import urllib.request
import uuid


def _multipart_body(field_name: str, file_path: pathlib.Path, boundary: str) -> tuple[bytes, str]:
    content_type = mimetypes.guess_type(file_path.name)[0] or 'application/octet-stream'
    file_bytes = file_path.read_bytes()
    lines = [
        f'--{boundary}'.encode(),
        f'Content-Disposition: form-data; name="{field_name}"; filename="{file_path.name}"'.encode(),
        f'Content-Type: {content_type}'.encode(),
        b'',
        file_bytes,
        f'--{boundary}--'.encode(),
        b'',
    ]
    body = b'\r\n'.join(lines)
    return body, f'multipart/form-data; boundary={boundary}'


def _request_json(url: str) -> dict:
    req = urllib.request.Request(url, method='GET')
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))


def _post_file(url: str, file_path: pathlib.Path) -> tuple[int, dict]:
    boundary = f'----SmokeBoundary{uuid.uuid4().hex}'
    body, content_type = _multipart_body('file', file_path, boundary)
    req = urllib.request.Request(url, data=body, method='POST')
    req.add_header('Content-Type', content_type)
    req.add_header('Content-Length', str(len(body)))
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.status, json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode('utf-8', errors='replace')
        try:
            parsed = json.loads(payload)
        except json.JSONDecodeError:
            parsed = {'raw_error': payload}
        return exc.code, parsed


def _print_result_summary(result: dict) -> None:
    summary = {
        'request_id': result.get('request_id'),
        'status': result.get('status'),
        'message': result.get('message'),
        'qc': result.get('qc'),
        'prediction': result.get('prediction'),
        'outputs': result.get('outputs'),
        'artifacts': result.get('artifacts'),
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(description='Smoke test for the FastAPI /health and /infer endpoints.')
    parser.add_argument('--base-url', default='http://127.0.0.1:8000', help='Base URL of the running API.')
    parser.add_argument('--dicom', type=pathlib.Path, help='Path to a valid DICOM file for ACCEPT/ACCEPT_WITH_WARNINGS smoke test.')
    parser.add_argument('--invalid-file', type=pathlib.Path, help='Path to an invalid/non-DICOM file for REJECT smoke test.')
    args = parser.parse_args()

    base_url = args.base_url.rstrip('/')

    print('[1/3] Checking /health ...')
    health = _request_json(f'{base_url}/health')
    print(json.dumps(health, indent=2, ensure_ascii=False))

    if args.dicom:
        print('\n[2/3] Checking /infer with valid DICOM ...')
        status, result = _post_file(f'{base_url}/infer', args.dicom)
        print(f'HTTP {status}')
        _print_result_summary(result)
        if status != 200:
            print('Expected HTTP 200 for a valid DICOM smoke test.', file=sys.stderr)
            return 1
        if result.get('status') not in {'ACCEPT', 'ACCEPT_WITH_WARNINGS'}:
            print('Expected ACCEPT or ACCEPT_WITH_WARNINGS for valid DICOM smoke test.', file=sys.stderr)
            return 1

    if args.invalid_file:
        print('\n[3/3] Checking /infer with invalid payload ...')
        status, result = _post_file(f'{base_url}/infer', args.invalid_file)
        print(f'HTTP {status}')
        _print_result_summary(result)
        if status != 200:
            print('Expected HTTP 200 with structured REJECT payload for invalid input smoke test.', file=sys.stderr)
            return 1
        if result.get('status') != 'REJECT':
            print('Expected REJECT for invalid input smoke test.', file=sys.stderr)
            return 1

    print('\nSmoke test finished.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
