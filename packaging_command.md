#### 32비트 플랫폼으로 변경
```
conda config --env --set subdir win-32
```
#### 환경 설치 및 파이썬, pip 설치
```
conda create -p .\py38 python=3.8.8 pip=21.0.1
```
#### 설치된 가상환경 목록 확인
```
conda env list
```
#### 가상환경 활성화
```
conda activate .\py38
```
#### 가상환경 플랫폼을 32비트로 고정
```
set CONDA_SUBDIR=win-32
```
#### 가상환경 플랫폼이 32비트가 맞는지 확인
```
conda info
```
#### 파이썬, pip 버전 확인
```
python -V
pip -V
```
#### 파이썬 인터프리터도 32비트로 설치되었는지 확인
```
python
import platform
platform.architecture()
exit()
```
#### 필요한 패키지들 설치
```
pip install -r requirements.txt
```
#### 설치된 패키지들 목록과 버전 확인
```
pip list
```
#### 실행 파일 패키징
```
pyinstaller --windowed --onefile --clean --icon="icon.ico" --add-data="icon.ico;." --name="box_scanner_gui.exe" box_scanner_gui.py
pyinstaller --console --onefile --clean --icon="icon.ico" --add-data="icon.ico;." --name="box_scanner_cli.exe" box_scanner_cli.py
```
#### 가상환경 비활성화
```
conda deactivate
```
