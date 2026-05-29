from __future__ import annotations

import io
from urllib.parse import urljoin

import requests
import streamlit as st
from PIL import Image

st.set_page_config(page_title='RSNA Image Client', page_icon='🩻', layout='centered')

DEFAULT_BACKEND_URL = 'http://127.0.0.1:8000'
DISPLAY_MAX_WIDTH = 900
REQUEST_TIMEOUT = 180


def build_absolute_url(base_url: str, relative_or_absolute: str | None) -> str | None:
    if not relative_or_absolute:
        return None
    return urljoin(base_url.rstrip('/') + '/', relative_or_absolute.lstrip('/'))


@st.cache_data(show_spinner=False)
def fetch_image(url: str) -> Image.Image:
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content)).convert('RGBA')


@st.cache_data(show_spinner=False)
def fetch_bytes(url: str) -> bytes:
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.content


@st.cache_data(show_spinner=False)
def resize_for_display(image: Image.Image, max_width: int = DISPLAY_MAX_WIDTH) -> Image.Image:
    width, height = image.size
    if width <= max_width:
        return image
    ratio = max_width / float(width)
    new_size = (max_width, max(1, int(height * ratio)))
    return image.resize(new_size, Image.LANCZOS)


@st.cache_data(show_spinner=False)
def compose_overlay(base_image: Image.Image, transparent_heatmap: Image.Image) -> Image.Image:
    base_rgba = base_image.convert('RGBA')
    heatmap_rgba = transparent_heatmap.convert('RGBA')
    if heatmap_rgba.size != base_rgba.size:
        heatmap_rgba = heatmap_rgba.resize(base_rgba.size, Image.LANCZOS)
    return Image.alpha_composite(base_rgba, heatmap_rgba)


def fetch_json(url: str) -> dict:
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response.json()


def render_prediction_badge(label: str | None) -> None:
    normalized = (label or 'N/A').strip().lower()
    if normalized == 'positive':
        bg = '#fde2e1'
        fg = '#b42318'
    elif normalized == 'negative':
        bg = '#dcfae6'
        fg = '#067647'
    else:
        bg = '#f2f4f7'
        fg = '#344054'

    st.markdown('**Pathology prediction**')
    st.markdown(
        f"""
        <div style="display:inline-block;padding:0.45rem 0.8rem;border-radius:0.6rem;background:{bg};color:{fg};font-weight:700;font-size:1rem;margin:0.15rem 0 0.8rem 0;">
            {label or 'N/A'}
        </div>
        """,
        unsafe_allow_html=True,
    )
    target_class = st.session_state.get('last_target_class')
    if normalized == 'positive' and target_class:
        st.caption(f'{target_class.capitalize()} detected.')
    elif normalized == 'negative' and target_class:
        st.caption(f'No {target_class.capitalize()} detected.')


def display_result(result: dict, backend_url: str, display_width: int, show_raw_json: bool) -> None:
    status = result.get('status')
    message = result.get('message')
    prediction = result.get('prediction') or {}
    st.session_state['last_target_class'] = prediction.get('target_class')
    qc = result.get('qc') or {}
    outputs = result.get('outputs') or {}
    artifacts = result.get('artifacts') or {}
    dicom_meta = qc.get('dicom_meta') or {}
    source_type = dicom_meta.get('source_type') or 'dicom'

    st.subheader('Inference result')
    col_a, col_b = st.columns([1, 1.4])
    with col_a:
        st.metric('Status', status or 'N/A')
    with col_b:
        render_prediction_badge(prediction.get('label'))

    if message:
        color = '#b42318' if status == 'REJECT' else '#067647'
        st.markdown(f"<span style='color:{color};font-weight:600'>{message}</span>", unsafe_allow_html=True)

    pred_col_1, pred_col_2 = st.columns(2)
    pred_col_1.metric('Probability', f"{prediction.get('probability'):.5f}" if prediction.get('probability') is not None else 'N/A')
    pred_col_2.metric('Confidence', f"{prediction.get('confidence'):.5f}" if prediction.get('confidence') is not None else 'N/A')

    with st.expander('Study metadata', expanded=True):
        left, right = st.columns(2)
        with left:
            st.write({
                'source_type': source_type,
                'modality': dicom_meta.get('modality'),
                'original_rows': dicom_meta.get('rows') or dicom_meta.get('original_rows'),
                'original_columns': dicom_meta.get('columns') or dicom_meta.get('original_columns'),
                'photometric_interpretation': dicom_meta.get('photometric_interpretation'),
            })
        with right:
            st.write({
                'reject_reasons': qc.get('reject_reasons'),
                'warnings': qc.get('warnings'),
                'summary': qc.get('summary'),
                'report_url': artifacts.get('report_url'),
                'derived_dicom_url': artifacts.get('derived_dicom_url'),
            })

    original_url = build_absolute_url(backend_url, outputs.get('original_image_url'))
    contour_url = build_absolute_url(backend_url, outputs.get('transparent_contour_url'))
    transparent_heatmap_url = build_absolute_url(backend_url, outputs.get('transparent_heatmap_url'))
    transparent_url = contour_url or transparent_heatmap_url
    overlay_url = build_absolute_url(backend_url, outputs.get('overlay_url'))
    analyzed_url = build_absolute_url(backend_url, outputs.get('image_analyzed_url'))
    heatmap_url = build_absolute_url(backend_url, outputs.get('heatmap_url'))
    derived_dicom_url = build_absolute_url(backend_url, artifacts.get('derived_dicom_url'))

    if status in {'ACCEPT', 'ACCEPT_WITH_WARNINGS'}:
        st.subheader('Visual outputs')

        if original_url:
            try:
                original_img = fetch_image(original_url)
                original_disp = resize_for_display(original_img, max_width=display_width)
                show_overlay = False
                if transparent_url:
                    show_overlay = st.toggle('Show Grad-CAM overlay on original image', value=True, key='show_overlay')
                if show_overlay and transparent_url:
                    transparent_img = fetch_image(transparent_url)
                    composed = compose_overlay(original_img, transparent_img)
                    display_img = resize_for_display(composed, max_width=display_width)
                    caption = 'Original image with overlay'
                else:
                    display_img = original_disp
                    caption = 'Original image'
                st.image(display_img, caption=caption, use_container_width=False)
            except Exception as exc:
                st.error(f'Could not render the main visual output: {exc}')

        detail_images = []
        for label, url in [('Model input image (224x224)', analyzed_url), ('Heatmap (224x224)', heatmap_url), ('Overlay (224x224)', overlay_url)]:
            if url:
                try:
                    detail_images.append((label, resize_for_display(fetch_image(url), max_width=min(display_width, 500))))
                except Exception:
                    pass
        if detail_images:
            with st.expander('Additional generated images', expanded=False):
                cols = st.columns(len(detail_images))
                for col, (label, img) in zip(cols, detail_images):
                    with col:
                        st.image(img, caption=label, use_container_width=True)

        if source_type == 'dicom' and derived_dicom_url:
            try:
                st.download_button(
                    label='Download analyzed DICOM',
                    data=fetch_bytes(derived_dicom_url),
                    file_name='derived_result.dcm',
                    mime='application/dicom',
                )
            except Exception as exc:
                st.warning(f'Could not download derived DICOM: {exc}')

            if st.button('Store analyzed study in Orthanc', key='store_in_orthanc'):
                try:
                    store_url = backend_url.rstrip('/') + f"/orthanc/runs/{artifacts.get('run_id')}/store-derived"
                    response = requests.post(store_url, timeout=REQUEST_TIMEOUT)
                    response.raise_for_status()
                    st.success(response.json().get('message', 'Derived DICOM stored in Orthanc.'))
                except Exception as exc:
                    st.error(f'Could not store the derived DICOM in Orthanc: {exc}')

    if show_raw_json:
        st.subheader('Raw JSON response')
        st.json(result)


if 'last_result' not in st.session_state:
    st.session_state.last_result = None
if 'last_backend_url' not in st.session_state:
    st.session_state.last_backend_url = DEFAULT_BACKEND_URL
if 'last_filename' not in st.session_state:
    st.session_state.last_filename = None
if 'last_source_mode' not in st.session_state:
    st.session_state.last_source_mode = 'Upload local file'

st.title('Pneumonia / lung opacity detection service')
st.caption('RSNA Image Client : Simple client for the external FastAPI service and Orthanc integration')

with st.sidebar:
    st.header('Settings')
    backend_url = st.text_input('Backend URL', value=st.session_state.last_backend_url)
    display_width = st.slider('Display width', min_value=320, max_value=1400, value=900, step=20)
    show_raw_json = st.checkbox('Show raw JSON response', value=False)
    source_mode = st.radio('Source mode', ['Upload local file', 'Select study from Orthanc'], index=0 if st.session_state.last_source_mode == 'Upload local file' else 1)

uploaded_file = None
selected_study_id = None

if source_mode == 'Upload local file':
    uploaded_file = st.file_uploader('Upload a DICOM or standard image file', type=['dcm', 'png', 'jpg', 'jpeg'])
else:
    if st.button('Refresh Orthanc study list'):
        st.cache_data.clear()

    studies_url = backend_url.rstrip('/') + '/orthanc/studies'
    try:
        studies = fetch_json(studies_url)
        options = {
            f"{s.get('study_id')} | {s.get('study_date') or '-'} | {s.get('patient_name') or '-'} | {s.get('study_description') or '-'}": s.get('study_id')
            for s in studies
        }
        if options:
            selected_label = st.selectbox('Orthanc studies', list(options.keys()))
            selected_study_id = options[selected_label]
        else:
            st.info('No studies available in Orthanc.')
    except Exception as exc:
        st.warning(f'Could not load studies from Orthanc: {exc}')

    if st.button('Analyze all pending Orthanc studies', type='secondary'):
        batch_url = backend_url.rstrip('/') + '/orthanc/batch/infer-unprocessed'
        with st.spinner('Running batch analysis for pending Orthanc studies...'):
            try:
                response = requests.post(batch_url, timeout=REQUEST_TIMEOUT)
                response.raise_for_status()
                batch_result = response.json()

                st.success(batch_result.get('message', 'Batch analysis completed.'))

                col1, col2, col3, col4 = st.columns(4)
                col1.metric('Total studies', batch_result.get('total_studies', 0))
                col2.metric('Already analyzed', batch_result.get('already_analyzed', 0))
                col3.metric('Processed now', batch_result.get('processed_now', 0))
                col4.metric('Failed', batch_result.get('failed', 0))

                col5, col6, col7 = st.columns(3)
                col5.metric('Positive cases', batch_result.get('positive_cases', 0))
                col6.metric('Negative cases', batch_result.get('negative_cases', 0))
                col7.metric('Rejected cases', batch_result.get('rejected_cases', 0))

                with st.expander('Batch details', expanded=False):
                    st.json(batch_result)

            except Exception as exc:
                st.error(f'Batch request failed: {exc}')

analyze_disabled = (uploaded_file is None) if source_mode == 'Upload local file' else (selected_study_id is None)
analyze_clicked = st.button('Analyze', type='primary', disabled=analyze_disabled)

if analyze_clicked:
    st.session_state.last_backend_url = backend_url
    st.session_state.last_source_mode = source_mode
    with st.spinner('Running inference...'):
        try:
            if source_mode == 'Upload local file' and uploaded_file is not None:
                infer_url = backend_url.rstrip('/') + '/infer'
                file_name = uploaded_file.name or 'input'
                file_ext = file_name.split('.')[-1].lower() if '.' in file_name else ''
                content_type = 'application/dicom' if file_ext == 'dcm' else (uploaded_file.type or 'application/octet-stream')
                files = {'file': (file_name, uploaded_file.getvalue(), content_type)}
                response = requests.post(infer_url, files=files, timeout=REQUEST_TIMEOUT)
                st.session_state.last_filename = uploaded_file.name
            else:
                infer_url = backend_url.rstrip('/') + '/orthanc/infer'
                response = requests.post(infer_url, json={'study_id': selected_study_id}, timeout=REQUEST_TIMEOUT)
                st.session_state.last_filename = selected_study_id

            if response.status_code == 409:
                detail = None
                try:
                    detail = response.json().get('detail')
                except Exception:
                    detail = response.text
                st.warning(detail or 'This Orthanc study has already been analyzed.')
                st.stop()

            response.raise_for_status()
            st.session_state.last_result = response.json()

        except Exception as exc:
            st.error(f'Backend request failed: {exc}')
            st.stop()


result = st.session_state.last_result
active_backend_url = st.session_state.last_backend_url
if result is not None:
    if st.session_state.last_filename:
        st.caption(f"Showing latest result for: {st.session_state.last_filename}")
    display_result(result, active_backend_url, display_width, show_raw_json)
