import sys

sys.stdout.write('stdout: %s' % sys.argv[2])
sys.stderr.write('stderr: %s' % sys.argv[2])
sys.exit(int(sys.argv[1]))
