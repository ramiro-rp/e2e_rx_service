from PIL import Image

from dicom_service.src.image_io import image_to_uint8_array
from dicom_service.src.image_qc import evaluate_image_qc


def test_image_qc_accepts_valid_standard_image():
    img = Image.new('RGB', (256, 256), color=(120, 120, 120))
    # add some variation
    for x in range(0, 256, 8):
        img.putpixel((x, x), (255, 255, 255))
    arr = image_to_uint8_array(img)
    result = evaluate_image_qc(img, arr)
    assert result.status in {'ACCEPT', 'ACCEPT_WITH_WARNINGS'}


def test_image_qc_rejects_near_constant_image():
    img = Image.new('RGB', (256, 256), color=(0, 0, 0))
    arr = image_to_uint8_array(img)
    result = evaluate_image_qc(img, arr)
    assert result.status == 'REJECT'
    assert 'near_constant_image' in result.reject_reasons
