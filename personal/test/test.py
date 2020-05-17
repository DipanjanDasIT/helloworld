import pytest
import random
from unittest.mock import patch, Mock
import math
import pyglet
import sys
from pyglet.graphics import *
from pyglet.gl import *
from pyglet.window import key
from main import main
from main import setup
from main import setup_fog
from main import Window, Model
from main import GRASS, JUMP_SPEED, FACES, WALKING_SPEED, GRAVITY, TERMINAL_VELOCITY, FLYING_SPEED
from main import sectorize
from main import normalize
from main import tex_coords
from main import tex_coord
from main import cube_vertices

def rand_choice(max=10, min=0, pres = 1):
    return random.choice(range(min, max))/pres

def create_vertices(x, y, z, n):
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,
    ]
def test_cube_vertices():
    """
    Function Tested: cube_vertices
    Purpose of tested function: Return the vertices of the cube at position x, y, z with size 2*n.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    x, y, z, n = rand_choice(), rand_choice(), rand_choice(), rand_choice()
    res = cube_vertices(x, y, z, n)
    assert type(res) == list and len(res) == (4*6*3) and res == create_vertices(x, y, z, n)

def test_tex_coord():
    """
    Function Tested: tex_coord
    Purpose of tested function: Return the bounding vertices of the texture square.
    Purpose of unittest: To check whether proper output is retruning or not
    """
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
    """
    Function Tested: tex_coords
    Purpose of tested function: Return a list of the texture squares for the top, bottom and side.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    mock_tex_coord.return_value = (0, 0.1, 0.2, 0.1, 0.2, 0.3, 0, 0.3)
    res = tex_coords((), (), ())
    assert type(res) == list and len(res) == 48

def test_normalize():
    """
    Function Tested: normalize
    Purpose of tested function: Accepts `position` of arbitrary precision and returns the block containing that position.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    position = (rand_choice(pres=0.1), rand_choice(pres=0.4), rand_choice(pres=0.11))
    res = normalize(position)
    assert type(res) == tuple and len(res) == 3 and all([type(i)==int for i in res])

@patch('main.normalize')
def test_sectorize(mock_normalize):
    """
    Function Tested: sectorize
    Purpose of tested function: Returns a tuple representing the sector for the given `position`.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    mock_normalize.return_value = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    position = (rand_choice(pres=0.1), rand_choice(pres=0.4), rand_choice(pres=0.11))
    res = sectorize(position)
    assert type(res) == tuple and len(res) == 3

def test_Model_initialize():
    """
    Function Tested: _initialize (Model Class)
    Purpose of tested function: Initialize the world by placing all the blocks.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    mock_model = Model()
    model_attrib_list = ['batch', 'group', 'world', 'shown', '_shown', 'sectors', 'queue']
    assert all([hasattr(mock_model, i) for i in model_attrib_list])
    assert len(mock_model.world) > 0 and len(mock_model.sectors) > 0
    assert len(mock_model.shown) == 0 and len(mock_model._shown) == 0
    assert len(mock_model.queue) == 0

@patch('main.normalize')
def test_Model_hit_test(mock_normalize):
    """
    Function Tested: hit_test (Model Class)
    Purpose of tested function: Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    existing_block_position_in_world = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    non_existing_block_in_world = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    dummy_vector = (rand_choice(max=2, pres=56),rand_choice(max=2, pres=1), rand_choice(max=2, pres=5))
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    mock_normalize.return_value = existing_block_position_in_world
    model_mock.world = {existing_block_position_in_world: ()}
    res = model_mock.hit_test(existing_block_position_in_world, dummy_vector)
    assert type(res) == tuple and len(res) == 2 and res[0] == existing_block_position_in_world 
    mock_normalize.return_value = non_existing_block_in_world
    res = model_mock.hit_test(non_existing_block_in_world, dummy_vector, max_distance=2)
    assert type(res) == tuple and len(res) == 2 and res == (None, None)

def test_Model_exposed():
    """
    Function Tested: exposed (Model Class)
    Purpose of tested function: Returns False is given `position` is surrounded on all 6 sides by
        blocks, True otherwise.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    model_mock.world = {FACES[0]:()}
    res = model_mock.exposed(position)
    assert res == True
    model_mock.world = {(face[0]+position[0], face[1]+position[1], face[2]+position[2]):() for face in FACES}
    res = model_mock.exposed(position)
    assert res == False

@patch('main.sectorize')
def test_Model_add_block(mock_sectorize):
    """
    Function Tested: add_block (Model Class)
    Purpose of tested function: Add a block with the given `texture` and `position` to the world.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
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
def test_Model_remove_block(mock_sectorize):
    """
    Function Tested: remove_block (Model Class)
    Purpose of tested function: Remove the block at the given `position`.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
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

def test_Model_check_neighbors():
    """
    Function Tested: check_neighbors (Model Class)
    Purpose of tested function: Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
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

def test_Model_show_block():
    """
    Function Tested: show_block (Model Class)
    Purpose of tested function: Show the block at the given `position`. This method assumes the
        block has already been added with add_block()
    Purpose of unittest: To check whether proper output is retruning or not
    """
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
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
def test_Model__show_block(mock_cube_vertices):
    """
    Function Tested: _show_block (Model Class)
    Purpose of tested function: Private implementation of the `show_block()` method.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    mock_cube_vertices.return_value = [i for i in range(4*3*6)]
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    model_mock._show_block(position, GRASS)
    assert position in model_mock._shown and type(model_mock._shown[position]) == pyglet.graphics.vertexdomain.VertexList

def test_Model_hide_block():
    """
    Function Tested: hide_block (Model Class)
    Purpose of tested function: Hide the block at the given `position`. Hiding does not remove the
        block from the world.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
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

def test_Model__hide_block():
    """
    Function Tested: _hide_block (Model Class)
    Purpose of tested function: Private implementation of the 'hide_block()` method.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    dummy_mock = Mock()
    dummy_mock.return_value.delete.return_value = None
    model_mock._shown = {position: dummy_mock}
    model_mock._hide_block(position)
    assert position not in model_mock._shown

def test_Model_show_sector():
    """
    Function Tested: show_sector (Model Class)
    Purpose of tested function: Ensure all blocks in the given sector that should be shown are
        drawn to the canvas.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    model_mock.sectors = {(1, 1, 1): [position]}
    model_mock.exposed = Mock(return_value=True)
    model_mock.show_block = lambda x, y: model_mock.queue.append((model_mock._show_block, tuple(x)))
    model_mock.show_sector((1, 1, 1))
    assert position == model_mock.queue[0][1]

def test_Model_hide_sector():
    """
    Function Tested: hide_sector (Model Class)
    Purpose of tested function: Ensure all blocks in the given sector that should be hidden are
        removed from the canvas.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    model_mock.sectors = {(1, 1, 1): [position]}
    model_mock.shown = {position, None}
    model_mock.hide_block = lambda x, y: model_mock.queue.append((model_mock._hide_block, x))
    model_mock.hide_sector((1, 1, 1))
    assert position == model_mock.queue[0][1]

def test_Model_change_sectors():
    """
    Function Tested: change_sectors (Model Class)
    Purpose of tested function: Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    func_call_trace = set()
    expected_call_trace = set(["hide_sector", "show_sector"])
    model_mock.show_sector = lambda x: func_call_trace.add("show_sector")
    model_mock.hide_sector = lambda x: func_call_trace.add("hide_sector")
    model_mock.change_sectors((2, 0, 5), (1, 0, 8))
    assert len(expected_call_trace.difference(func_call_trace)) == 0


def test_Model__enqueue():
    """
    Function Tested: _enqueue (Model Class)
    Purpose of tested function: Add `func` to the internal queue.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    model_mock._enqueue(model_mock._show_block, position)
    assert len(model_mock.queue) > 0

def test_Model__dequeue():
    """
    Function Tested: _dequeue (Model Class)
    Purpose of tested function: Pop the top function from the internal queue and call it.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    dummy_mock = Mock()
    dummy_mock.return_value.delete.return_value = None
    model_mock._shown = {position: dummy_mock}
    model_mock._hide_block = lambda x, y, z: model_mock._shown.pop((x, y, z)).delete()
    model_mock.queue.append((model_mock._hide_block, position))
    queue_len = len(model_mock.queue)
    model_mock._dequeue()
    assert len(model_mock.queue) == queue_len - 1 and len(model_mock._shown) == 0


def test_Model_process_queue():
    """
    Function Tested: process_queue (Model Class)
    Purpose of tested function: Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False
    Purpose of unittest: To check whether proper output is retruning or not
    """
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    for i in range(2):
        model_mock.queue.append({i: i})
    model_mock._dequeue = lambda : model_mock.queue.pop()
    model_mock.process_queue()
    assert len(model_mock.queue) == 0

def test_Model_process_entire_queue():
    """
    Function Tested: process_entire_queue (Model Class)
    Purpose of tested function: Process the entire queue with no breaks.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    Model._initialize = Mock(return_value=None)
    model_mock = Model()
    for i in range(10):
        model_mock.queue.append({i: i})
    model_mock._dequeue = lambda : model_mock.queue.pop()
    model_mock.process_queue()
    assert len(model_mock.queue) == 0

def test_Window_set_exclusive_mouse():
    """
    Function Tested: set_exclusive_mouse (Window Class)
    Purpose of tested function: If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    win_mock.set_exclusive_mouse(True)
    assert win_mock.exclusive == True
    win_mock.set_exclusive_mouse(False)
    assert win_mock.exclusive == False

def test_Window_get_sight_vector():
    """
    Function Tested: get_sight_vector (Window Class)
    Purpose of tested function: Returns the current line of sight vector indicating the direction
        the player is looking.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    p, q = rand_choice(), rand_choice()
    m = math.cos(math.radians(q))
    dy = math.sin(math.radians(q))
    dx = math.cos(math.radians(p - 90)) * m
    dz = math.sin(math.radians(p - 90)) * m
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    win_mock.rotation = (p, q)
    res = win_mock.get_sight_vector()
    assert (dx, dy, dz) == res


def test_Window_get_motion_vector():
    """
    Function Tested: get_motion_vector (Window Class)
    Purpose of tested function: Returns the current motion vector indicating the velocity of the
        player.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    win_mock.strafe = [0, 0]
    res = win_mock.get_motion_vector()
    assert (0.0, 0.0, 0.0) == res
    win_mock.strafe = [0, 1]
    rx, ry = win_mock.rotation
    strafe = math.degrees(math.atan2(*win_mock.strafe))
    y_angle = math.radians(ry)
    x_angle = math.radians(rx + strafe)
    win_mock.flying = False
    res = win_mock.get_motion_vector()
    assert (math.cos(x_angle), 0.0, math.sin(x_angle) ) == res
    win_mock.flying = True
    m = math.cos(y_angle)
    dy = math.sin(y_angle)
    dy = 0.0
    m = 1
    dx = math.cos(x_angle) * m
    dz = math.sin(x_angle) * m
    res = win_mock.get_motion_vector()
    assert (dx, dy, dz) == res

@patch('main.sectorize')
def test_Window_update(mock_sectorize):
    """
    Function Tested: update (Window Class)
    Purpose of tested function: This method is scheduled to be called repeatedly by the pyglet
        clock.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    win_mock.model.process_queue = Mock(return_value=None)
    mock_sectorize.return_value = (1, 0, 1)
    win_mock.model.change_sectors = Mock(return_value=None)
    win_mock.model.process_entire_queue = Mock(return_value=None)
    update_stack = []
    win_mock._update = lambda x: update_stack.append("_update")
    win_mock.update(2)
    assert win_mock.sector == (1, 0, 1) and len(update_stack) == 8


def test_Window__update():
    """
    Function Tested: _update (Window Class)
    Purpose of tested function: Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    dt = 1
    dx, dy, dz = 2, 4, 5
    win_mock.get_motion_vector = Mock(return_value=(dx, dy, dz))
    d = dt * WALKING_SPEED
    dx, dy, dz = dx * d, dy * d, dz * d
    new_position = (6, 7, 8)
    win_mock.collide = Mock(return_value=new_position)
    win_mock.flying = True
    win_mock._update(dt)
    assert win_mock.position == new_position
    win_mock.flying = False
    dx, dy, dz = 2, 4, 5
    d = dt * FLYING_SPEED
    dx, dy, dz = dx * d, dy * d, dz * d
    wdy = win_mock.dy
    wdy -= dt * GRAVITY
    wdy = max(wdy, -TERMINAL_VELOCITY)
    win_mock._update(dt)
    assert win_mock.dy == wdy

@patch('main.normalize')
def test_Window_collide(mock_normalize):
    """
    Function Tested: collide (Window Class)
    Purpose of tested function: Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world
    Purpose of unittest: To check whether proper output is retruning or not
    """
    if sys.version_info[0] >= 3:
        xrange = range
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    pad = 0.25
    height = 4
    p = list(position)
    np = (int(round(position[0])), int(round(position[1])), int(round(position[2])))
    for face in FACES:
        for i in xrange(3):
            if not face[i]:
                continue
            d = (p[i] - np[i]) * face[i]
            if d < pad:
                continue
            for dy in xrange(height):
                op = list(np)
                op[1] -= dy
                op[i] += face[i]
                if tuple(op) not in self.model.world:
                    continue
                p[i] -= (d - pad) * face[i]
                if face in [(0, -1, 0), (0, 1, 0)]:
                    self.dy = 0
                break
    mock_normalize.return_value = position
    res = win_mock.collide(position, height)
    assert res == tuple(p)

def test_Window_on_mouse_press():
    """
    Function Tested: on_mouse_press (Window Class)
    Purpose of tested function: Called when a mouse button is pressed. See pyglet docs for button
        amd modifier mappings.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    win_mock.exclusive = False
    win_mock.on_mouse_press(None, None, 1, None)
    assert win_mock.exclusive == True
    win_mock.get_sight_vector = Mock(return_value=(1, 0, 1))
    win_mock.model.hit_test = Mock(return_value=(1, 1))
    func_call_trace = []
    win_mock.model.add_block = lambda x, y: func_call_trace.append("model.add_block")
    win_mock.model.world[1] = None
    win_mock.model.remove_block = lambda x: func_call_trace.append("model.remove_block")
    win_mock.on_mouse_press(None, None, 1, 0)
    assert "model.remove_block" == func_call_trace[0]
    win_mock.on_mouse_press(None, None, 4, None)
    assert "model.add_block" == func_call_trace[1]

def test_Window_on_mouse_motion():
    """
    Function Tested: on_mouse_motion (Window Class)
    Purpose of tested function: Called when the player moves the mouse.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    m = 0.15
    dx, dy = 2, 3
    o, q = dx * m, dy * m
    q = max(-90, min(90, q))
    win_mock.exclusive = False
    win_mock.on_mouse_motion(None, None, dx, dy)
    assert win_mock.rotation == (0,0)
    win_mock.exclusive = True
    win_mock.on_mouse_motion(None, None, dx, dy)
    assert win_mock.rotation == (o, q)

def test_Window_on_key_press():
    """
    Function Tested: on_key_press (Window Class)
    Purpose of tested function: Called when the player presses a key. See pyglet docs for key
        mappings.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    win_mock.on_key_press(key.W, None)
    assert [-1, 0] == win_mock.strafe
    win_mock.on_key_press(key.S, None)
    assert [0, 0] == win_mock.strafe
    win_mock.on_key_press(key.A, None)
    assert [0, -1] == win_mock.strafe
    win_mock.on_key_press(key.D, None)
    assert [0, 0] == win_mock.strafe
    win_mock.on_key_press(key.SPACE, None)
    assert win_mock.dy == JUMP_SPEED
    out_obj = []
    win_mock.set_exclusive_mouse = lambda x: out_obj.append("set_exclusive_mouse is called")
    win_mock.on_key_press(key.ESCAPE, None)
    assert "set_exclusive_mouse is called" in out_obj
    assert win_mock.exclusive == False
    cur_flying = win_mock.flying
    win_mock.on_key_press(key.TAB, None)
    assert win_mock.flying == (not cur_flying)
    win_mock.on_key_press(key._8, None)
    assert win_mock.block == GRASS

def test_Window_on_key_release():
    """
    Function Tested: on_key_release (Window Class)
    Purpose of tested function: Called when the player releases a key. See pyglet docs for key
        mappings.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    win_mock.on_key_release(key.W, None)
    assert [1, 0] == win_mock.strafe
    win_mock.on_key_release(key.S, None)
    assert [0, 0] == win_mock.strafe
    win_mock.on_key_release(key.A, None)
    assert [0, 1] == win_mock.strafe
    win_mock.on_key_release(key.D, None)
    assert [0, 0] == win_mock.strafe

def test_Window_on_resize():
    """
    Function Tested: on_resize (Window Class)
    Purpose of tested function: Called when the window is resized to a new `width` and `height`.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    new_height, new_width = random.choice(range(1, y)), random.choice(range(1, x))
    win_mock.on_resize(new_width, new_height)
    assert win_mock.label.y == new_height - 10
    assert type(win_mock.reticle) == pyglet.graphics.vertexdomain.VertexList
    out_obj = []
    win_mock.reticle.delete = lambda : out_obj.append("reticle.delete has been called")
    win_mock.on_resize(new_width, new_height)
    assert "reticle.delete has been called" in out_obj

@pytest.mark.skip("set_2d function is setting up configuration of gl can not be part of unittest")
def test_Window_set_2d():
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    win_mock.set_2d()

@pytest.mark.skip("set_3d function is setting up configuration of gl can not be part of unittest")
def test_Window_set_3d():
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    win_mock.set_3d()

def test_Window_on_draw():
    """
    Function Tested: on_draw (Window Class)
    Purpose of tested function: Called by pyglet to draw the canvas.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    func_call_trace = []
    expected_call_trcae = ["clear", "set_3d", "model.batch.draw", "draw_focused_block",
                            "set_2d", "draw_label", "draw_reticle"]
    win_mock.clear = lambda : func_call_trace.append("clear")
    win_mock.set_3d = lambda : func_call_trace.append("set_3d")
    win_mock.model.batch.draw = lambda : func_call_trace.append("model.batch.draw")
    win_mock.draw_focused_block = lambda : func_call_trace.append("draw_focused_block")
    win_mock.set_2d = lambda : func_call_trace.append("set_2d")
    win_mock.draw_label = lambda : func_call_trace.append("draw_label")
    win_mock.draw_reticle = lambda : func_call_trace.append("draw_reticle")
    win_mock.on_draw()
    assert func_call_trace == expected_call_trcae

@patch('pyglet.graphics')
@patch('main.cube_vertices')
def test_Window_draw_focused_block(mock_cube_vertices, mock_graph):
    """
    Function Tested: draw_focused_block (Window Class)
    Purpose of tested function: Draw black edges around the block that is currently under the
        crosshairs.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    dummy_vector = (rand_choice(max=2, pres=56),rand_choice(max=2, pres=1), rand_choice(max=2, pres=5))
    position = (rand_choice(min=16, max=25), rand_choice(), rand_choice(min=55, max=500))
    x, y = 800, 600
    Model._initialize = Mock(return_value=None)
    win_mock = Window(height=y, width=x)
    win_mock.get_sight_vector = Mock(return_value=dummy_vector)
    m, n, p = position
    out_obj = {}
    mock_cube_vertices.return_value = create_vertices(m, n, p, 0.51)
    mock_graph.draw = lambda a, b, c: out_obj.update({"message": "pyglet.graphics.draw() has been called"})
    win_mock.model.hit_test = Mock(return_value=(None, None))
    win_mock.draw_focused_block()
    assert len(out_obj) == 0
    win_mock.model.hit_test = Mock(return_value=(position, None))
    win_mock.draw_focused_block()
    assert "pyglet.graphics.draw() has been called" in out_obj.values()

def test_Window_draw_label():
    """
    Function Tested: draw_label (Window Class)
    Purpose of tested function: Draw the label in the top left of the screen.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    Model._initialize = Mock(return_value=None)
    x, y = 80, 60
    win_mock = Window(height=x, width=y)
    win_mock.position = (0, 0, 0)
    out_obj = {}
    win_mock.label.draw = lambda : out_obj.update({"message": "label.draw() is been called"})
    win_mock.draw_label()
    assert " %d / %d" % (len(win_mock.model._shown), len(win_mock.model.world)) in win_mock.label.text
    assert "label.draw() is been called" in out_obj.values()

def test_Window_draw_reticle():
    """
    Function Tested: draw_reticle (Window Class)
    Purpose of tested function: Draw the crosshairs in the center of the screen.
    Purpose of unittest: To check whether proper output is retruning or not
    """
    x, y = 80, 60
    n = 10
    Model._initialize = Mock(return_value=None)
    win_mock = Window(height=x, width=y)
    win_mock.reticle = pyglet.graphics.vertex_list(4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )
    out_obj = {}
    win_mock.reticle.draw = lambda x: out_obj.update({"message": "draw funcion has been called with argument " + str(x) })
    win_mock.draw_reticle()
    assert "draw funcion has been called with argument " + str(GL_LINES) in out_obj.values()

@pytest.mark.skip("setup_fog function is setting up configuration of gl can not be part of unittest")
def test_setup_fog():
    setup_fog()

@pytest.mark.skip("setup function is setting up configuration of gl can not be part of unittest")
def test_setup():
    setup()

@patch('pyglet.app')
@patch('main.setup')
@patch('main.Window')
def test_main(mock_window, mock_setup, mock_app):
    """
    Function Tested: main
    Purpose of tested function: Starting point of the program
    Purpose of unittest: To check whether proper output is retruning or not
    """
    func_call_trace = set()
    expected_func_call = set(["set_exclusive_mouse", "setup", "pyglet.app.run"])
    mock_window.return_value.set_exclusive_mouse = lambda s: func_call_trace.add('set_exclusive_mouse')
    mock_setup.return_value = func_call_trace.add('setup')
    mock_app.run = lambda : func_call_trace.add('pyglet.app.run')
    main()
    assert expected_func_call == func_call_trace
    
