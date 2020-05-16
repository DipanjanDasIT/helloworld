import pytest
import random
from unittest.mock import patch, Mock
import os
import traceback
import pyglet

def rand_choice(max=10, min=0, pres = 1):
    return random.choice(range(min, max))/pres

def test_cube_vertices():
    from main import cube_vertices
    x, y, z, n = rand_choice(), rand_choice(), rand_choice(), rand_choice()
    res = cube_vertices(x, y, z, n)
    assert type(res) == list and len(res) == (4*6*3)

def test_tex_coord():
    from main import tex_coord
    x, y, n = rand_choice(), rand_choice(), rand_choice()
    try:
        res =  tex_coord(x, y, n)
        assert type(res) == tuple and len(res) == 8
    except ZeroDivisionError as ex:
        assert n==0

    x, y = rand_choice(), rand_choice()
    res =  tex_coord(x, y)
    assert type(res) == tuple and len(res) == 8

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

@patch('main.normalize')
@patch('pyglet.image')
def test_Model_hit_test(mock_image_load, mock_normalize):
    existing_block_position_in_world = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    non_existing_block_in_world = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    dummy_vector = (rand_choice(max=2, pres=56),rand_choice(max=2, pres=1), rand_choice(max=2, pres=5))
    mock_normalize.return_value = existing_block_position_in_world
    from main import Model
    mock_image_load.load.return_value.get_texture.return_value = None
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    model_mock.world = {existing_block_position_in_world: ()}
    res = model_mock.hit_test(existing_block_position_in_world, dummy_vector)
    assert type(res) == tuple and len(res) == 2 and res[0] == existing_block_position_in_world 
    mock_normalize.return_value = non_existing_block_in_world
    res = model_mock.hit_test(non_existing_block_in_world, dummy_vector, max_distance=2)
    assert type(res) == tuple and len(res) == 2 and res == (None, None)

@patch('pyglet.image')
def test_Model_exposed(mock_image_load):
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    from main import Model, FACES
    mock_image_load.load.return_value.get_texture.return_value = None
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    model_mock.world = {FACES[0]:()}
    res = model_mock.exposed(position)
    assert res == True
    model_mock.world = {(face[0]+position[0], face[1]+position[1], face[2]+position[2]):() for face in FACES}
    res = model_mock.exposed(position)
    assert res == False

@patch('main.sectorize')
@patch('pyglet.image')
def test_Model_add_block(mock_image_load, mock_sectorize):
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    from main import Model, FACES
    mock_image_load.load.return_value.get_texture.return_value = None
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    model_mock.world = {}
    dummy_sector = (rand_choice(min=16, max=25), 0, rand_choice(min=16, max=25))
    mock_sectorize.return_value = dummy_sector
    model_mock.add_block(position, "TEXTURE", False)
    assert position in model_mock.world and position in model_mock.sectors[dummy_sector]
    model_mock.sectors = {}
    model_mock.remove_block = Mock(return_value=None)
    model_mock.add_block(position, "NEW_TEXTURE", False)
    assert position in model_mock.world and position in model_mock.sectors[dummy_sector]
    assert model_mock.world[position] == "NEW_TEXTURE"
    model_mock.sectors = {}
    model_mock.exposed = Mock(return_value=True)
    model_mock.show_block = lambda x: model_mock.shown.update(model_mock.world)
    model_mock.check_neighbors = Mock(return_value=None)
    dummy_texture = "IMMEDIATE_NEW_TEXTURE"
    model_mock.add_block(position, dummy_texture)
    assert model_mock.shown[position] == dummy_texture

@patch('main.sectorize')
@patch('pyglet.image')
def test_Model_remove_block(mock_image_load, mock_sectorize):
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    from main import Model, FACES
    mock_image_load.load.return_value.get_texture.return_value = None
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    model_mock.world[position] = "Texture"
    with patch.dict(model_mock.sectors, {(): [position]}):
        mock_sectorize.return_value = ()
        model_mock.remove_block(position, False)
        assert position not in model_mock.world and position not in model_mock.sectors[()]
    model_mock.world[position] = "IMMEDIATE_Texture"
    with patch.dict(model_mock.sectors, {(): [position]}):
        with patch.dict(model_mock.shown, model_mock.world):
            mock_sectorize.return_value = ()
            model_mock.hide_block = lambda x: model_mock.shown.pop(x)
            model_mock.check_neighbors = Mock(return_value=None)
            model_mock.remove_block(position)
            assert position not in model_mock.world and position not in model_mock.sectors[()]
            assert position not in model_mock.shown

@patch('pyglet.image')
def test_Model_check_neighbors(mock_image_load):
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    from main import Model, FACES
    mock_image_load.load.return_value.get_texture.return_value = None
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    model_mock.world[FACES[0]] = None
    model_mock.shown = {}
    model_mock.check_neighbors(position)
    assert model_mock.shown == {}
    dummy_key = (position[0]+FACES[0][0], position[1]+FACES[0][1], position[2]+FACES[0][2])
    model_mock.world = {dummy_key: None}
    model_mock.exposed = Mock(return_value=True)
    model_mock.show_block = lambda x: model_mock.shown.update({x: model_mock.world[x]})
    model_mock.check_neighbors(position)
    assert dummy_key in model_mock.shown
    model_mock.exposed = Mock(return_value=False)
    model_mock.hide_block = lambda x: model_mock.shown.pop(x)
    model_mock.check_neighbors(position)
    assert dummy_key not in model_mock.shown

@patch('pyglet.image')
def test_Model_show_block(mock_image_load):
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    from main import Model
    mock_image_load.load.return_value.get_texture.return_value = None
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    model_mock.world = {position: "Texture"}
    model_mock._enqueue = lambda f, *a: model_mock.queue.append((f, a))
    model_mock.show_block(position, False)
    assert position in model_mock.shown and position in model_mock.queue[0][1]
    model_mock._show_block = lambda x, y: model_mock._shown.update({x: y})
    model_mock.show_block(position)
    assert position in model_mock.shown and position in model_mock._shown
    
@patch('main.cube_vertices')
@patch('pyglet.image')
def test_Model__show_block(mock_image_load, mock_cube_vertices):
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    mock_cube_vertices.return_value = [i for i in range(4*3*6)]
    from main import Model, GRASS
    mock_image_load.load.return_value.get_texture.return_value = Mock()
    mock_image_load.load.return_value.get_texture.return_value.target = None
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    model_mock._show_block(position, GRASS)
    assert position in model_mock._shown and type(model_mock._shown[position]) == pyglet.graphics.vertexdomain.VertexList

@patch('pyglet.image')
def test_Model_hide_block(mock_image_load):
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    from main import Model
    mock_image_load.load.return_value.get_texture.return_value = None
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    model_mock.shown = {position: None}
    model_mock._enqueue = lambda f, *a: model_mock.queue.append((f, a))
    model_mock.hide_block(position, False)
    assert position not in model_mock.shown and  position in model_mock.queue[0][1]
    model_mock.shown = {position: None}
    dummy_mock = Mock()
    dummy_mock.return_value.delete.return_value = None
    model_mock._shown = {position: dummy_mock}
    model_mock._hide_block = lambda x: model_mock._shown.pop(x).delete()
    model_mock.hide_block(position)
    assert position not in model_mock.shown and position not in model_mock._shown

@patch('pyglet.image')
def test_Model__hide_block(mock_image_load):
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    from main import Model
    mock_image_load.load.return_value.get_texture.return_value = None
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    dummy_mock = Mock()
    dummy_mock.return_value.delete.return_value = None
    model_mock._shown = {position: dummy_mock}
    model_mock._hide_block(position)
    assert position not in model_mock._shown

@patch('pyglet.image')
def test_Model_show_sector(mock_image_load):
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    from main import Model
    mock_image_load.load.return_value.get_texture.return_value = None
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    model_mock.sectors = {(1, 1, 1): [position]}
    model_mock.exposed = Mock(return_value=True)
    model_mock.show_block = lambda x, y: model_mock.queue.append((model_mock._show_block, tuple(x)))
    model_mock.show_sector((1, 1, 1))
    assert position == model_mock.queue[0][1]


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
