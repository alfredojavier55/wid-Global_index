# wid-Global_index
D5.3 – Global index representing the overall burden of diseases, including economic, social, welfare, and epidemiological aspects
Description:
Global index of the burden of animal infectious diseases (including direct losses, compensation, denied access to international markets, etc.) and the applications to the 2 case studies

## Literature review: 

Use pubmed2csv.py to transform pubmed text file to a column csv version (check imput-output)

Use clasifier.ipyn to classify and extract using the promt on a jupiter notebook (ollama library)

Using Miniconda:
   \ 1  conda env list
   \ 2  curl -O https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh
   \ 3  wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
   \ 4  bash ~/Miniconda3-latest-Linux-x86_64.sh
   \ 5  conda config --set auto_activate_base false
   \ 6  ll /JumpStorage/Alfredo/
   \ 7  watch -n 0.1 nvidia-smi
   \ 8  ollama
   \ 9  ollama run  llama3.3
   \10  conda create -n ollama python=3.10
   \11  conda activate ollama
   \12  pip install ollama
   \13  pip install pandas
   \14  python pubmed2csv
