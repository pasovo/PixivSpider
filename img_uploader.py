import os
import requests
import configparser
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_upload_config(config_file="./config.ini"):
    config = configparser.ConfigParser()
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"配置文件未找到: {config_file}")
    try:
        config.read(config_file, encoding="utf-8")
        if "upload" not in config:
            raise KeyError("配置文件缺少 'upload' 部分")
        upload = config["upload"]
        return {
            "api_url": upload.get("api_url", "https://cfbed.sanyue.de/api/upload"),
            "img_dir": upload.get("img_dir", "./img"),
            "auth_code": upload.get("auth_code", ""),
            "server_compress": upload.get("server_compress", "true"),
            "upload_channel": upload.get("upload_channel", "telegram"),
            "auto_retry": upload.get("auto_retry", "true"),
            "upload_name_type": upload.get("upload_name_type", "default"),
            "return_format": upload.get("return_format", "default"),
            "upload_folder": upload.get("upload_folder", ""),
            "max_workers": int(upload.get("max_workers", "5"))
        }
    except Exception as e:
        raise RuntimeError(f"配置文件解析错误: {e}")

def upload_image(image_path, cfg):
    params = {
        "authCode": cfg["auth_code"],
        "serverCompress": cfg["server_compress"],
        "uploadChannel": cfg["upload_channel"],
        "autoRetry": cfg["auto_retry"],
        "uploadNameType": cfg["upload_name_type"],
        "returnFormat": cfg["return_format"],
        "uploadFolder": cfg["upload_folder"]
    }
    # 去除空参数
    params = {k: v for k, v in params.items() if v}
    with open(image_path, "rb") as f:
        files = {"file": f}
        response = requests.post(cfg["api_url"], files=files, params=params)
        try:
            result = response.json()
        except requests.exceptions.JSONDecodeError:
            result = {"error": "响应不是JSON", "text": response.text}
        return result

def batch_upload(config_file="config.ini"):
    cfg = get_upload_config(config_file)
    img_files = [fname for fname in os.listdir(cfg["img_dir"]) if os.path.isfile(os.path.join(cfg["img_dir"], fname))]
    results = {}
    with ThreadPoolExecutor(max_workers=cfg["max_workers"]) as executor:
        future_to_fname = {executor.submit(upload_image, os.path.join(cfg["img_dir"], fname), cfg): fname for fname in img_files}
        for future in as_completed(future_to_fname):
            fname = future_to_fname[future]
            try:
                res = future.result()
            except Exception as e:
                res = {"error": str(e)}
            results[fname] = res
            print(f"上传: {fname}")
            print(f"结果: {res}")
    return results

if __name__ == "__main__":
    batch_upload()
