# secure-distributed-file-storage-hdfs

#  Distributed File Storage System (FastAPI + HDFS)

##  Overview
A distributed file storage system that supports encrypted, chunked file uploads using FastAPI and Hadoop HDFS. The system is containerized with Docker and uses Nginx to load balance across multiple backend instances, simulating a scalable production architecture.

---

##  Architecture
User → Nginx (Load Balancer) → FastAPI (3 instances)
↓
PostgreSQL (metadata)
↓
WebHDFS API
↓
HDFS (NameNode + DataNode)


### Key Components
- **Nginx** → Distributes incoming requests across backend instances  
- **FastAPI** → Handles authentication, file operations, and orchestration  
- **PostgreSQL** → Stores metadata (users, files, chunk locations)  
- **HDFS (WebHDFS)** → Stores actual file chunks in a distributed manner  

---

## ⚙️ Tech Stack
- **Backend:** FastAPI  
- **Database:** PostgreSQL  
- **Storage:** Hadoop HDFS (WebHDFS REST API)  
- **Load Balancer:** Nginx  
- **Containerization:** Docker & Docker Compose  
- **Security:** JWT Authentication + File Encryption (Fernet)  

---

##  How It Works

###  Upload Flow
1. User uploads a file via the UI  
2. File is temporarily stored on the server  
3. File is encrypted using a user-specific key  
4. Encrypted file is split into 200KB chunks  
5. Each chunk is uploaded to HDFS via WebHDFS  
6. Metadata is stored in PostgreSQL:
   - file info  
   - chunk order  
   - HDFS paths  
7. Temporary files are deleted  

---

###  Download Flow
1. System fetches chunk metadata from PostgreSQL  
2. All chunks are downloaded from HDFS  
3. Chunks are merged into a single encrypted file  
4. File is decrypted using the owner’s key  
5. Final file is returned to the user  

---

##  Key Features
- Chunk-based file upload system  
- End-to-end file encryption & decryption  
- Distributed storage using HDFS  
- Load-balanced backend using Nginx  
- Role-based access control (Student / Teacher)  
- Metadata tracking with PostgreSQL  
- Multi-container microservices architecture  

---

##  Design Decisions
- **HDFS over local storage**  
  → Simulates real-world distributed storage systems  

- **Chunking files**  
  → Enables handling large uploads and improves scalability  

- **Encryption layer**  
  → Ensures data security at rest  

- **Nginx load balancing**  
  → Demonstrates horizontal scaling across multiple backend instances  

- **Service-layer architecture**  
  → Separates concerns (encryption, chunking, HDFS interaction)  

---

##  Project Structure
cloudexam/
│
├── main.py
├── docker-compose.yml
├── nginx.conf
├── Dockerfile
├── requirements.txt
│
├── app/
│ ├── core/ # auth, config
│ ├── db/ # models, session
│ ├── routes/ # API endpoints
│ ├── services/ # encryption, chunking, HDFS logic
│ └── ui/ # HTML pages
│
└── storage/ # temp + chunk + merged files


---

##  Run Locally

```bash
docker compose up --build
```
-Then open:
http://localhost:8000

---
###  Screenshots

<img width="1919" height="816" alt="image" src="https://github.com/user-attachments/assets/fea95851-609a-420f-bb72-11719d430475" />
<img width="1919" height="782" alt="image" src="https://github.com/user-attachments/assets/016f494b-4ab5-4ba9-89ec-81b86c788782" />
<img width="1870" height="909" alt="image" src="https://github.com/user-attachments/assets/422eba56-01a6-4b06-b7f9-6c76a1c71898" />
<img width="1901" height="906" alt="image" src="https://github.com/user-attachments/assets/7147889e-7b9f-4376-be44-c6384729ea1f" />
<img width="1913" height="793" alt="image" src="https://github.com/user-attachments/assets/0edd30fa-81af-4e7a-a094-0a013d99d430" />
<img width="1916" height="832" alt="image" src="https://github.com/user-attachments/assets/3f961ad2-640d-40d8-b921-77fa951aeb2e" />
<img width="1908" height="874" alt="image" src="https://github.com/user-attachments/assets/dacc997f-dd06-4136-af4e-6426ebe7b554" />
<img width="1908" height="875" alt="image" src="https://github.com/user-attachments/assets/027cc7ed-1976-43b1-94bc-abdc16741262" />

---

###  Detailed Walkthrough
- For deeper technical explanation:
    cloud_exam_system_explained.ipynb

###  What This Project Demonstrates
  1. Distributed systems understanding
  2. Backend system design
  3. File processing pipelines
  4. Containerized deployment
  5. Load balancing & scaling concepts
  6. Secure data handling
