
class Contents(object):
    #flag = " ⚑ "
    flag = " f "
    mine = " b "
    empty = "   "
    smile = " :)"

def set_ascii():
    Contents.flag = ' f '
    Contents.mine = ' b '
    Contents.smile = ' :)'

# Don't actually call these (for now) because then server and client side might
# differ, and that would be bad.
def set_unicode():
    Contents.flag = ' ⚑ '
    Contents.mine = ' 💣 '
    Contents.smile = ' ☺ '
