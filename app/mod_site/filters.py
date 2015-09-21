# Basic filter to strip all whitespace from a string
def id_escape(string):
    return ''.join(''.join(string.split('/')).split())


# Filter that replaces all 'M' with 'Gents' and 'F' with 'Ladies'
def expand_gender(string):
    if string[0] == 'M':
        return 'Gents' + string[1:]
    else:
        return 'Ladies' + string[1:]
