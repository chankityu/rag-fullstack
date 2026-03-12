This is a full complete RAG chatbot. 

This chatbot takes documentation in forms of txt. file or PDF. Put the documents that you want the RAG to learn into ```docs``` folder.

There are two sides. First is the front end Next JS stack. To set this up, cd into ```front-end-app``` folder and do ```npm run dev```

The second part is the Python FastAPI backend. To set this up, cd into ```backend``` folder.

Then, install the required Python packages through

```
pip install -r requirements.txt
```

Then, simply start the server using command

```
fastapi dev main.py --host 0.0.0.0
```

![2026-03-12 15-12-17](https://github.com/user-attachments/assets/875bb1aa-6a2a-4cf1-b55e-cc7a82005a87)

Then you can load the front end and the chatbot is ready.


![2026-03-12 15-24-27](https://github.com/user-attachments/assets/a8643887-5538-47de-ac03-9e10b4d4655e)
