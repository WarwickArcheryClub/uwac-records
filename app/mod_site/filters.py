# Basic filter to strip all whitespace from a string
def strip_spaces(str):
    return "".join(str.split())


# Filter that replaces all 'M' with 'Gents' and 'F' with 'Ladies'
def expand_gender(str):
    if str[0] == 'M':
        return 'Gents' + str[1:]
    else:
        return 'Ladies' + str[1:]
