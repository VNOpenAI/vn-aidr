# VN AIDr - Open source medical image processing project

Project documentation (only Vietnamese): <https://dr.vnopenai.org/>.

This project contains baseline models for medical image processing and a web user interface for interacting with the system. Our goal is to create an open source code base for students, hobbylists, engineers, or even researchers to get familar with image processing, machine learning and deep learning through medical image processing problems. In this system, we also integrate natural language processing (NLP) models for automatic completion of medical reports.

Want to join us in this project? Send us a message via [our contact form](https://vnopenai.org/contact/).

![VN AIDr - Prediction](screenshots/screen.png)
## Requirements

- Python 3.7 + Pip
- NodeJS
- Yarn
- Detectron2: <https://detectron2.readthedocs.io/en/latest/tutorials/install.html>

## 1. Server 

- Download pretrained models [here](https://drive.google.com/drive/folders/1TtcVLluJhGSNIrAGoT1txQA1ob78lFFp?usp=sharing) and extract them into `trained_models`.

```
pip install -r requirements.txt
python app.py
```

- Open `http://localhost:5000` in your browser.


## 2. Frontend (UI)

### Development

```
cd frontend
yarn
yarn start
```

### Build

```
cd frontend
yarn
yarn build
```

## Copyright and License

The template was developed based on [SB Admin 2](https://startbootstrap.com/theme/sb-admin-2).
