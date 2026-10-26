import sys
import traceback
import run_b6_golden

try:
    run_b6_golden.main()
except BaseException as e:
    with open('error.log', 'w') as f:
        traceback.print_exc(file=f)
        f.write("\nBaseException: " + str(e))
