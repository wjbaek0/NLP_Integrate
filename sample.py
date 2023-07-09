import subprocess
import sys

result = subprocess.run(['/home/xaiplanet/xai_workspace/nlp_integrate/sample.sh', sys.argv[0]], capture_output=True, text=True).stdout
# result = subprocess.run(['/home/xaiplanet/xai_workspace/nlp_integrate/CausalRelation/_03_causal_test.py', sys.argv], capture_output=True, text=True).stdout
# result = subprocess.run(['/home/xaiplanet/xai_workspace/nlp_integrate/sample_run.py'], shell=True)
print(result)
