from bot.parser import Parser
from bot.storage import Storage

text = """
ABC123
DEF456
abc123
Hello World
WWMGO1115
"""

codes = Parser.extract_codes(text)

print(codes)

for code in codes:
    print(code, Storage.is_new(code))

Storage.add_codes(codes)

print(Storage.load_codes())
