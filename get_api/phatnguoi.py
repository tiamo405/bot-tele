import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

from utils.retry_decorator import retry_on_exception


PHATNGUOI_API_URL = "https://phatnguoi.app/wp-admin/admin-ajax.php"
PHATNGUOI_ACTION = "phatnguoi_search"
PHATNGUOI_NONCE = "eac6d4a9a0"
VALID_VEHICLE_TYPES = {"car", "moto"}


def normalize_plate(license_plate: str) -> str:
    """Chuẩn hóa biển số nhập vào."""
    if not license_plate:
        return ""

    plate = license_plate.strip().upper()
    plate = plate.replace("–", "-")
    plate = " ".join(plate.split())
    return plate


@retry_on_exception(max_retries=2, delay=1.0, exceptions=(requests.RequestException,))
def _search_by_vehicle_type(license_plate: str, vehicle_type: str) -> dict:
    """Gọi API với vehicle_type cụ thể (car/moto)."""
    payload = {
        "action": PHATNGUOI_ACTION,
        "nonce": PHATNGUOI_NONCE,
        "license_plate": license_plate,
        "vehicle_type": vehicle_type,
    }

    response = requests.post(PHATNGUOI_API_URL, data=payload, timeout=20)
    response.raise_for_status()

    result = response.json()
    if not isinstance(result, dict):
        raise ValueError("Invalid API response format")

    success = bool(result.get("success"))
    data = result.get("data") if isinstance(result.get("data"), dict) else {}
    message = result.get("message") or ""

    return {
        "success": success,
        "data": data,
        "message": str(message),
        "vehicle_type": vehicle_type,
    }


def _pick_best_result(results: dict) -> dict:
    """Chọn kết quả phù hợp nhất khi tra cứu cả car và moto."""
    candidates = [res for res in results.values() if res.get("success")]
    if not candidates:
        return {}

    def score(item: dict) -> tuple:
        data = item.get("data") or {}
        total = int(data.get("total_violations") or 0)
        unpaid = int(data.get("unpaid_count") or 0)
        return (1 if total > 0 else 0, unpaid, total)

    # Nếu bằng nhau thì ưu tiên car để ổn định
    best = max(candidates, key=lambda item: (score(item), 1 if item.get("vehicle_type") == "car" else 0))
    return best


def search_phat_nguoi(license_plate: str, vehicle_type: str = "auto") -> dict:
    """
    Tra cứu phạt nguội theo biển số.

    Args:
        license_plate: Biển số xe
        vehicle_type: car/moto/auto

    Returns:
        Dict kết quả chuẩn hóa:
        {
            "success": bool,
            "data": dict,
            "message": str,
            "vehicle_type": "car"|"moto"|"auto"
        }
    """
    plate = normalize_plate(license_plate)
    if not plate:
        return {
            "success": False,
            "data": {},
            "message": "Biển số không hợp lệ",
            "vehicle_type": "auto",
        }

    normalized_type = (vehicle_type or "auto").strip().lower()

    if normalized_type in VALID_VEHICLE_TYPES:
        try:
            result = _search_by_vehicle_type(plate, normalized_type)
            return result
        except Exception as exc:
            return {
                "success": False,
                "data": {},
                "message": f"Không thể tra cứu lúc này: {exc}",
                "vehicle_type": normalized_type,
            }

    # Auto mode: thử cả car và moto
    trial_results = {}
    errors = []

    for vt in ("car", "moto"):
        try:
            trial_results[vt] = _search_by_vehicle_type(plate, vt)
        except Exception as exc:
            errors.append(f"{vt}: {exc}")

    best = _pick_best_result(trial_results)
    if best:
        return best

    error_message = "; ".join(errors) if errors else "Không có dữ liệu"
    return {
        "success": False,
        "data": {},
        "message": f"Không thể tra cứu lúc này ({error_message})",
        "vehicle_type": "auto",
    }
