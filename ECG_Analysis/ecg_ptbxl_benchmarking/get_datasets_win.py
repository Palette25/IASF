import os
import sys
import shutil
from pathlib import Path
from urllib.request import urlretrieve
from zipfile import ZipFile


PTBXL_ZIP_URL = "https://physionet.org/content/ptb-xl/get-zip/1.0.3/"

ICBEB_FILES = {
    "REFERENCE.csv": "http://2018.icbeb.org/file/REFERENCE.csv",
    "TrainingSet1.zip": "http://hhbucket.oss-cn-hongkong.aliyuncs.com/TrainingSet1.zip",
    "TrainingSet2.zip": "http://hhbucket.oss-cn-hongkong.aliyuncs.com/TrainingSet2.zip",
    "TrainingSet3.zip": "http://hhbucket.oss-cn-hongkong.aliyuncs.com/TrainingSet3.zip",
}


def download_file(url: str, target: Path):
    if target.exists():
        print(f"[skip] 已存在: {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    print(f"[download] {url}")
    print(f"           -> {target}")
    urlretrieve(url, str(target))
    print("[done] 下载完成\n")


def unzip_file(zip_path: Path, dest_dir: Path):
    print(f"[unzip] {zip_path} -> {dest_dir}")
    dest_dir.mkdir(parents=True, exist_ok=True)
    with ZipFile(str(zip_path), "r") as zf:
        zf.extractall(str(dest_dir))
    print("[done] 解压完成\n")


def prepare_ptbxl(base_dir: Path):
    data_dir = base_dir / "data"
    data_dir.mkdir(exist_ok=True)

    zip_path = data_dir / "ptbxl.zip"
    download_file(PTBXL_ZIP_URL, zip_path)

    unzip_file(zip_path, data_dir)

    # 原 zip 解压后的目录名
    src_dir = data_dir / "ptb-xl-a-large-publicly-available-electrocardiography-dataset-1.0.1"
    dst_dir = data_dir / "ptbxl"
    if src_dir.exists() and not dst_dir.exists():
        print(f"[move] {src_dir} -> {dst_dir}")
        src_dir.rename(dst_dir)
        print("[done] 重命名完成\n")
    elif dst_dir.exists():
        print(f"[skip] 已存在目录: {dst_dir}\n")
    else:
        print("[warn] 未找到解压后的 PTB-XL 目录，请手动检查 data/ 目录结构。\n")


def prepare_icbeb(base_dir: Path):
    tmp_dir = base_dir / "tmp_data"
    tmp_dir.mkdir(exist_ok=True)

    # 下载 ICBEB 文件
    for name, url in ICBEB_FILES.items():
        download_file(url, tmp_dir / name)

    # 解压三个训练集
    for name in ["TrainingSet1.zip", "TrainingSet2.zip", "TrainingSet3.zip"]:
        zip_path = tmp_dir / name
        if zip_path.exists():
            unzip_file(zip_path, tmp_dir)
        else:
            print(f"[warn] 未找到 {zip_path}, 跳过解压。")

    # 调用原始的 convert_ICBEB.py
    convert_script = base_dir / "code" / "utils" / "convert_ICBEB.py"
    if not convert_script.exists():
        raise FileNotFoundError(f"未找到脚本: {convert_script}")

    print(f"[run] python {convert_script}")
    ret = os.system(f'"{sys.executable}" "{convert_script}"')
    if ret != 0:
        raise RuntimeError("运行 convert_ICBEB.py 失败，请检查错误输出。")
    print("[done] ICBEB 转换完成\n")

    # 拷贝 scp_statements.csv
    src_csv = base_dir / "data" / "ptbxl" / "scp_statements.csv"
    dst_dir = base_dir / "data" / "ICBEB"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst_csv = dst_dir / "scp_statements.csv"

    if not src_csv.exists():
        raise FileNotFoundError(f"未找到 PTB-XL 的 scp_statements.csv: {src_csv}")

    print(f"[copy] {src_csv} -> {dst_csv}")
    shutil.copy(str(src_csv), str(dst_csv))
    print("[done] 拷贝完成\n")


def main():
    base_dir = Path(__file__).resolve().parent
    print(f"[info] 项目根目录: {base_dir}")

    print("=== 1. 准备 PTB-XL 数据集 ===")
    prepare_ptbxl(base_dir)

    print("=== 2. 准备 ICBEB 数据集 ===")
    prepare_icbeb(base_dir)

    print("全部数据集准备完成。")


if __name__ == "__main__":
    main()

