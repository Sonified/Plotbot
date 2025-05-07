#File: suppress_output.py

#I don't think these are really being utilized at the moment
#But they may be helpful in the future 🤷🏾‍♂️

# class StderrFilter:
#     def __init__(self, original_stderr):
#         self.original_stderr = original_stderr

#     def write(self, message):
#         if "+[CATransaction synchronize] called within transaction" not in message:
#             self.original_stderr.write(message)

#     def flush(self):
#         self.original_stderr.flush()

# # Apply the stderr filter
# #sys.stderr = StderrFilter(sys.stderr)
        
# Suppress the verbose output
@contextlib.contextmanager
def suppress_output():
    with open(os.devnull, 'w') as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr