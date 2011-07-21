
export PATH=/usr/local/git/bin/:$PATH
# /usr/local/bin/patience --config $HOME/resources.yaml list > repos.yaml
# 
python compute_stats.py < repos.yaml > dirs.yaml
python dump_files.py < dirs.yaml