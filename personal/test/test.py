import pytest
import random

def rand_choice(max=10, min=0):
    return random.choice(range(min, max))
def test_cube_vertices():
    from main import cube_vertices
    x, y, z, n = rand_choice(), rand_choice(), rand_choice(), rand_choice()
    res = cube_vertices(x, y, z, n)
    assert type(res) == list and len(res) == (4*6*3)

def test_tex_coord():
    from main import tex_coord
    x, y, n = rand_choice(), rand_choice(), rand_choice(max=1, min=0)
    try:
        res =  tex_coord(x, y, n)
        assert type(res) == tuple and len(res) == 8
    except ZeroDivisionError as ex:
        assert n==0

    x, y = rand_choice(), rand_choice()
    res =  tex_coord(x, y)
    assert type(res) == tuple and len(res) == 8 and all()

def test_tex_coords():
    pass

def test_normalize():
    pass

def test_sectorize():
    pass

def test_Model_initialize():
    pass

def test_Model_hit_test():
    pass

def test_Model_exposed():
    pass

def test_Model_add_block():
    pass

def test_Model_remove_block():
    pass

def test_Model_check_neighbors():
    pass

def test_Model_show_block():
    pass

def test_Model__show_block():
    pass

def test_Model_hide_block():
    pass

def test_Model__hide_block():
    pass

def test_Model_show_sector():
    pass

def test_Model_hide_sector():
    pass

def test_Model_change_sectors():
    pass

def test_Model__enqueue():
    pass

def test_Model__dequeue():
    pass

def test_Model_process_queue():
    pass

def test_Model_process_entire_queue():
    pass

def test_Window_set_exclusive_mouse():
    pass

def test_Window_get_sight_vector():
    pass

def test_Window_get_motion_vector():
    pass

def test_Window_update():
    pass

def test_Window__update():
    pass

def test_Window_collide():
    pass

def test_Window_on_mouse_press():
    pass

def test_Window_on_mouse_motion():
    pass

def test_Window_on_key_press():
    pass

def test_Window_on_key_release():
    pass

def test_Window_on_resize():
    pass

def test_Window_set_2d():
    pass

def test_Window_set_3d():
    pass

def test_Window_on_draw():
    pass

def test_Window_draw_focused_block():
    pass

def test_Window_draw_label():
    pass

def test_Window_draw_reticle():
    pass

def test_setup_fog():
    pass

def test_setup():
    pass

def test_main():
    pass
