For install:
-
git clone https://github.com/tonniteles/OltCloud 

Create Virtual Environment
-
python3 -m venv .venv

Install Requirements
-
source .venv/bin/activate  
pip install -r requirements.txt

Create .env
-
API_URL=https://myapp.oltcloud.co  
API_USER=api.user  
API_PASS=api.pass  
### Verify end of line
cat -A .env  
sed -i 's/\r$//' .env  

Script to start 
-
#!/bin/bash
source .venv/bin/activate  
nohup python import_onus.py &  
nohup streamlit run app.py --server.port 8500 &  

