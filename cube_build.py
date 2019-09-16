
def make_fancy_cube (**kwargs):
    name = kwargs.setdefault('name', 'Mr.Cube')
    size = kwargs.setdefault('size', 10 )
    return name, size



g_name, g_size = make_fancy_cube(name = 'tom')
print 'name;' + g_name
print 'size;' + str(g_size)