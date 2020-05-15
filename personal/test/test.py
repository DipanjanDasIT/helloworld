import pytest
import random
from unittest.mock import patch

def rand_choice(max=10, min=0, pres = 1):
    return random.choice(range(min, max))/pres
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

@patch('main.tex_coord')
def test_tex_coords(mock_tex_coord):
    mock_tex_coord.return_value = (0, 0.1, 0.2, 0.1, 0.2, 0.3, 0, 0.3)
    from main import tex_coords
    res = tex_coords((), (), ())
    assert type(res) == list and len(res) == 48

def test_normalize():
    position = (rand_choice(pres=0.1), rand_choice(pres=0.4), rand_choice(pres=0.11))
    from main import normalize
    res = normalize(position)
    assert type(res) == tuple and len(res) == 3 and all([type(i)==int for i in res])

@patch('main.normalize')
def test_sectorize(mock_normalize):
    mock_normalize.return_value = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    position = (rand_choice(pres=0.1), rand_choice(pres=0.4), rand_choice(pres=0.11))
    from main import sectorize
    res = sectorize(position)
    assert type(res) == tuple and len(res) == 3

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
