FROM node:18

WORKDIR /app
COPY package*.json ./
RUN npm install

# Install Tesseract for OCR
RUN apt-get update && apt-get install -y tesseract-ocr

COPY . .

CMD ["node", "src/index.js"]
