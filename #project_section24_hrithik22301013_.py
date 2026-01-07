#project_section24_hrithik22301013_ramisha22201693

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math

# Camera-related variables
camera_pos = [0, 800, 800]
camera_mode = 0  # 0: Bird's eye, 1: Follow vehicle, 2: Intersection view
fovY = 60
GRID_LENGTH = 600

# Environment variables
is_night = False
is_highway = False

# Speed Boost Zones
speed_zones = [
    {'x': -400, 'y': 0, 'width': 100, 'height': 240},  # Left zone
    {'x': 200, 'y': 0, 'width': 100, 'height': 240},   # Right zone
    {'x': 0, 'y': -400, 'width': 240, 'height': 100},  # Bottom zone
    {'x': 0, 'y': 200, 'width': 240, 'height': 100},   # Top zone
]
boost_active = False

# Traffic signal variables
signal_timer = 0
signal_state = 0  # 0: Red, 1: Yellow, 2: Green
manual_mode = False  # NEW: Flag for manual control
RED_TIME = 180      # Increased time - slower changes
YELLOW_TIME = 60
GREEN_TIME = 180

# Vehicle class
class Vehicle:
    def __init__(self, x, y, z, v_type, speed, direction, lane):
        self.x = x
        self.y = y
        self.z = z
        self.type = v_type  # 0: Car, 1: Bus, 2: Truck
        self.speed = speed
        self.base_speed = speed
        self.stopped = False
        self.warning = False
        self.direction = direction  # 0: horizontal (x+), 1: vertical (y+)
        self.lane = lane  # Lane offset to prevent collision

# Initialize vehicles on SEPARATE lanes
vehicles = [
    Vehicle(-600, 60, 0, 0, 2.5, 0, 60),     # Car - top lane
    Vehicle(-550, -60, 0, 1, 2.0, 0, -60),   # Bus - bottom lane
    Vehicle(60, -600, 0, 2, 1.8, 1, 60),     # Truck - right lane
    Vehicle(-60, -550, 0, 0, 2.3, 1, -60),   # Car - left lane
]

queue_count = 0


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    """Draw text on screen - ONLY uses functions from your code"""
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


# ============================================================================
# MEMBER 1 - FEATURE 1: Traffic Signal System with Timing
# ============================================================================
def draw_traffic_signal():
    """Draw traffic light with red/yellow/green lights and timing"""
    glPushMatrix()
    glTranslatef(200, 200, 0)
    
    # Pole (cylinder)
    glColor3f(0.2, 0.2, 0.2)
    glPushMatrix()
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 8, 150, 10, 10)
    glPopMatrix()
    
    # Signal box (cube)
    glTranslatef(0, 0, 150)
    glColor3f(0.15, 0.15, 0.15)
    glutSolidCube(50)
    
    # Red light (top) - sphere
    glTranslatef(0, 0, 35)
    if signal_state == 0:
        glColor3f(1, 0, 0)
    else:
        glColor3f(0.2, 0, 0)
    gluSphere(gluNewQuadric(), 15, 20, 20)
    
    # Yellow light (middle) - sphere
    glTranslatef(0, 0, -35)
    if signal_state == 1:
        glColor3f(1, 1, 0)
    else:
        glColor3f(0.2, 0.2, 0)
    gluSphere(gluNewQuadric(), 15, 20, 20)
    
    # Green light (bottom) - sphere
    glTranslatef(0, 0, -35)
    if signal_state == 2:
        glColor3f(0, 1, 0)
    else:
        glColor3f(0, 0.2, 0)
    gluSphere(gluNewQuadric(), 15, 20, 20)
    
    glPopMatrix()


# ============================================================================
# MEMBER 1 - FEATURE 2: Multiple Vehicle Types with Movement
# ============================================================================
def draw_vehicle(v_type, warning=False):
    """Draw different vehicle types using cube, cylinder, sphere, scale"""
    
    if v_type == 0:  # CAR
        # Body (cube)
        if warning:
            glColor3f(1, 0.3, 0.3)
        else:
            glColor3f(0.8, 0.1, 0.1)
        glutSolidCube(40)
        
        # Roof (scaled cube)
        glTranslatef(0, 0, 25)
        glScalef(0.7, 0.8, 0.5)
        glutSolidCube(40)
        glScalef(1/0.7, 1/0.8, 1/0.5)
        glTranslatef(0, 0, -25)
        
        # Wheels (cylinders)
        glColor3f(0.1, 0.1, 0.1)
        positions = [(15, 15, -12), (15, -15, -12), (-15, 15, -12), (-15, -15, -12)]
        for px, py, pz in positions:
            glPushMatrix()
            glTranslatef(px, py, pz)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 8, 8, 4, 10, 10)
            glPopMatrix()
    
    elif v_type == 1:  # BUS
        # Body (scaled cube)
        if warning:
            glColor3f(1, 0.5, 0.5)
        else:
            glColor3f(0.1, 0.3, 0.8)
        glScalef(1.6, 1.0, 1.2)
        glutSolidCube(45)
        glScalef(1/1.6, 1/1.0, 1/1.2)
        
        # Windows (scaled cube)
        glColor3f(0.3, 0.5, 0.7)
        glTranslatef(0, 0, 25)
        glScalef(1.4, 0.9, 0.3)
        glutSolidCube(45)
        glScalef(1/1.4, 1/0.9, 1/0.3)
        glTranslatef(0, 0, -25)
        
        # Wheels (cylinders)
        glColor3f(0.1, 0.1, 0.1)
        positions = [(30, 30, -20), (30, -30, -20), (-30, 30, -20), (-30, -30, -20)]
        for px, py, pz in positions:
            glPushMatrix()
            glTranslatef(px, py, pz)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 10, 10, 4, 10, 10)
            glPopMatrix()
    
    else:  # TRUCK
        # Cabin (cube)
        if warning:
            glColor3f(0.5, 1, 0.5)
        else:
            glColor3f(0.1, 0.6, 0.1)
        glTranslatef(25, 0, 0)
        glutSolidCube(38)
        
        # Cargo area (scaled cube)
        glTranslatef(-45, 0, 8)
        glScalef(1.6, 1.0, 1.4)
        glutSolidCube(45)
        glScalef(1/1.6, 1/1.0, 1/1.4)
        glTranslatef(45, 0, -8)
        glTranslatef(-25, 0, 0)
        
        # Wheels (cylinders)
        glColor3f(0.1, 0.1, 0.1)
        positions = [(35, 18, -18), (35, -18, -18), (-25, 18, -18), (-25, -18, -18)]
        for px, py, pz in positions:
            glPushMatrix()
            glTranslatef(px, py, pz)
            glRotatef(90, 0, 1, 0)
            gluCylinder(gluNewQuadric(), 9, 9, 4, 10, 10)
            glPopMatrix()


# ============================================================================
# MEMBER 1 - FEATURE 3: Road Network with Intersections
# ============================================================================
def draw_roads():
    """Draw roads using GL_QUADS with intersections and markings"""
    
    glBegin(GL_QUADS)
    
    # Main horizontal road
    if is_night:
        glColor3f(0.15, 0.15, 0.15)
    else:
        glColor3f(0.3, 0.3, 0.3)
    
    glVertex3f(-GRID_LENGTH, -120, 0)
    glVertex3f(GRID_LENGTH, -120, 0)
    glVertex3f(GRID_LENGTH, 120, 0)
    glVertex3f(-GRID_LENGTH, 120, 0)
    
    # Main vertical road
    glVertex3f(-120, -GRID_LENGTH, 0)
    glVertex3f(120, -GRID_LENGTH, 0)
    glVertex3f(120, GRID_LENGTH, 0)
    glVertex3f(-120, GRID_LENGTH, 0)
    
    # Intersection zone (lighter)
    if is_night:
        glColor3f(0.2, 0.2, 0.2)
    else:
        glColor3f(0.4, 0.4, 0.4)
    
    glVertex3f(-120, -120, 1)
    glVertex3f(120, -120, 1)
    glVertex3f(120, 120, 1)
    glVertex3f(-120, 120, 1)
    
    # Lane markings (white dashed)
    glColor3f(1, 1, 1)
    for i in range(-GRID_LENGTH, GRID_LENGTH, 60):
        if abs(i) > 130:
            glVertex3f(i, -3, 2)
            glVertex3f(i + 30, -3, 2)
            glVertex3f(i + 30, 3, 2)
            glVertex3f(i, 3, 2)
    
    for i in range(-GRID_LENGTH, GRID_LENGTH, 60):
        if abs(i) > 130:
            glVertex3f(-3, i, 2)
            glVertex3f(3, i, 2)
            glVertex3f(3, i + 30, 2)
            glVertex3f(-3, i + 30, 2)
    
    # Zebra crossings
    for i in range(-100, 100, 25):
        if (i // 25) % 2 == 0:
            glColor3f(1, 1, 1)
        else:
            glColor3f(0.9, 0.9, 0.9)
        glVertex3f(130, i, 2)
        glVertex3f(160, i, 2)
        glVertex3f(160, i + 20, 2)
        glVertex3f(130, i + 20, 2)
    
    for i in range(-100, 100, 25):
        if (i // 25) % 2 == 0:
            glColor3f(1, 1, 1)
        else:
            glColor3f(0.9, 0.9, 0.9)
        glVertex3f(i, 130, 2)
        glVertex3f(i + 20, 130, 2)
        glVertex3f(i + 20, 160, 2)
        glVertex3f(i, 160, 2)
    
    glEnd()


# ============================================================================
# MEMBER 2 - FEATURE 2: Speed Boost Zones
# ============================================================================
def draw_speed_zones():
    """Draw glowing green speed boost zones using GL_QUADS"""
    glBegin(GL_QUADS)
    
    for zone in speed_zones:
        x = zone['x']
        y = zone['y']
        w = zone['width']
        h = zone['height']
        
        # Glowing green zone
        glColor3f(0, 1, 0)
        glVertex3f(x - w/2, y - h/2, 3)
        glVertex3f(x + w/2, y - h/2, 3)
        glVertex3f(x + w/2, y + h/2, 3)
        glVertex3f(x - w/2, y + h/2, 3)
        
        # Border (yellow)
        glColor3f(1, 1, 0)
        # Top border
        glVertex3f(x - w/2 - 5, y + h/2, 3.5)
        glVertex3f(x + w/2 + 5, y + h/2, 3.5)
        glVertex3f(x + w/2 + 5, y + h/2 + 5, 3.5)
        glVertex3f(x - w/2 - 5, y + h/2 + 5, 3.5)
        
        # Bottom border
        glVertex3f(x - w/2 - 5, y - h/2 - 5, 3.5)
        glVertex3f(x + w/2 + 5, y - h/2 - 5, 3.5)
        glVertex3f(x + w/2 + 5, y - h/2, 3.5)
        glVertex3f(x - w/2 - 5, y - h/2, 3.5)
        
        # Left border
        glVertex3f(x - w/2 - 5, y - h/2, 3.5)
        glVertex3f(x - w/2, y - h/2, 3.5)
        glVertex3f(x - w/2, y + h/2, 3.5)
        glVertex3f(x - w/2 - 5, y + h/2, 3.5)
        
        # Right border
        glVertex3f(x + w/2, y - h/2, 3.5)
        glVertex3f(x + w/2 + 5, y - h/2, 3.5)
        glVertex3f(x + w/2 + 5, y + h/2, 3.5)
        glVertex3f(x + w/2, y + h/2, 3.5)
    
    glEnd()


def check_speed_boost():
    """Check if vehicles are in speed boost zones"""
    global boost_active
    boost_active = False
    
    for vehicle in vehicles:
        in_zone = False
        
        for zone in speed_zones:
            x = zone['x']
            y = zone['y']
            w = zone['width']
            h = zone['height']
            
            # Check if vehicle is inside zone
            if (vehicle.x > x - w/2 and vehicle.x < x + w/2 and
                vehicle.y > y - h/2 and vehicle.y < y + h/2):
                in_zone = True
                boost_active = True
                # Apply speed boost
                if not vehicle.stopped:
                    vehicle.speed = vehicle.base_speed * 1.8
                break
        
        # Reset to base speed if not in zone
        if not in_zone and not vehicle.stopped and not vehicle.warning:
            vehicle.speed = vehicle.base_speed


# ============================================================================
# MEMBER 2 - FEATURE 3: City vs Highway Environment Switch
# ============================================================================
def draw_street_lights():
    """Draw street lights using cylinder and sphere"""
    if not is_night:
        return
    
    positions = [
        (-350, -350), (350, -350),
        (-350, 350), (350, 350),
        (-250, 0), (250, 0),
        (0, -250), (0, 250)
    ]
    
    for px, py in positions:
        glPushMatrix()
        glTranslatef(px, py, 0)
        
        # Pole (cylinder)
        glColor3f(0.25, 0.25, 0.25)
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 4, 4, 120, 10, 10)
        glPopMatrix()
        
        # Light bulb (sphere)
        glTranslatef(0, 0, 120)
        glColor3f(1, 0.95, 0.7)
        gluSphere(gluNewQuadric(), 18, 15, 15)
        
        glPopMatrix()


# ============================================================================
# MEMBER 2 - FEATURE 3: City vs Highway Environment Switch
# ============================================================================
def draw_city_buildings():
    """Draw city buildings using scaled cubes and trees using cylinder+sphere"""
    
    # Buildings (scaled cubes)
    buildings = [
        (-450, 350, 120, 80, 80),
        (-450, -350, 150, 80, 80),
        (450, 350, 100, 80, 80),
        (450, -350, 130, 80, 80),
        (-350, 500, 90, 60, 60),
        (350, 500, 110, 60, 60),
        (-350, -500, 85, 60, 60),
        (350, -500, 95, 60, 60),
    ]
    
    for bx, by, height, width, depth in buildings:
        glPushMatrix()
        glTranslatef(bx, by, height/2)
        
        if is_night:
            glColor3f(0.2, 0.2, 0.3)
        else:
            glColor3f(0.5, 0.5, 0.6)
        
        glScalef(width, depth, height)
        glutSolidCube(1)
        glPopMatrix()
        
        # Windows at night (small cubes)
        if is_night:
            glColor3f(1, 1, 0.7)
            for h in range(20, int(height) - 20, 30):
                for w in range(-int(width/2) + 15, int(width/2), 20):
                    glPushMatrix()
                    glTranslatef(bx + w, by + depth/2 + 1, h)
                    glutSolidCube(8)
                    glPopMatrix()
    
    # Trees (cylinder trunk + sphere crown)
    tree_positions = [
        (-280, 280), (280, 280),
        (-280, -280), (280, -280),
        (-180, 0), (180, 0),
        (0, -180), (0, 180)
    ]
    
    for tx, ty in tree_positions:
        glPushMatrix()
        glTranslatef(tx, ty, 0)
        
        # Trunk (cylinder)
        glColor3f(0.4, 0.25, 0.1)
        glPushMatrix()
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 8, 8, 45, 10, 10)
        glPopMatrix()
        
        # Crown (sphere)
        glTranslatef(0, 0, 60)
        if is_night:
            glColor3f(0.05, 0.3, 0.05)
        else:
            glColor3f(0.1, 0.6, 0.1)
        gluSphere(gluNewQuadric(), 25, 15, 15)
        
        glPopMatrix()


def draw_highway_barriers():
    """Draw highway barriers using scaled cubes and cylinders"""
    
    # Left side barriers
    for i in range(-GRID_LENGTH, GRID_LENGTH, 80):
        glPushMatrix()
        glTranslatef(i, -280, 20)
        glColor3f(0.9, 0.9, 0.1)
        glScalef(70, 8, 40)
        glutSolidCube(1)
        glPopMatrix()
        
        # Support poles (cylinder)
        glPushMatrix()
        glTranslatef(i, -280, 0)
        glColor3f(0.3, 0.3, 0.3)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 3, 3, 20, 8, 8)
        glPopMatrix()
    
    # Right side barriers
    for i in range(-GRID_LENGTH, GRID_LENGTH, 80):
        glPushMatrix()
        glTranslatef(i, 280, 20)
        glColor3f(0.9, 0.9, 0.1)
        glScalef(70, 8, 40)
        glutSolidCube(1)
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(i, 280, 0)
        glColor3f(0.3, 0.3, 0.3)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), 3, 3, 20, 8, 8)
        glPopMatrix()


# ============================================================================
# MEMBER 2 - FEATURE 1: Collision Detection & Avoidance
# ============================================================================
def check_collisions():
    """Check distance between vehicles and trigger warnings/stops"""
    for i, v1 in enumerate(vehicles):
        v1.warning = False
        min_safe_distance = 120  # Safe distance between vehicles
        
        for j, v2 in enumerate(vehicles):
            if i != j:
                # Only check vehicles moving in same direction
                if v1.direction == v2.direction:
                    if v1.direction == 0:  # Horizontal
                        # Check if in same lane and if v1 is behind v2
                        if abs(v1.y - v2.y) < 50 and v2.x > v1.x and (v2.x - v1.x) < min_safe_distance:
                            v1.warning = True
                            v1.speed = v2.speed * 0.5  # Slow down
                            break
                    else:  # Vertical
                        # Check if in same lane and if v1 is behind v2
                        if abs(v1.x - v2.x) < 50 and v2.y > v1.y and (v2.y - v1.y) < min_safe_distance:
                            v1.warning = True
                            v1.speed = v2.speed * 0.5  # Slow down
                            break
        
        # Reset speed if no collision warning
        if not v1.warning and not v1.stopped:
            v1.speed = v1.base_speed


# ============================================================================
# MEMBER 2 - FEATURE 4: Vehicle Queue Management at Signals
# ============================================================================
def check_signal_stop():
    """Check if vehicles should stop at red light and count queue"""
    global queue_count
    queue_count = 0
    
    for vehicle in vehicles:
        # Only stop at red light
        if signal_state == 0:  # RED LIGHT
            # Horizontal vehicles approaching intersection
            if vehicle.direction == 0 and vehicle.x > 80 and vehicle.x < 200:
                vehicle.stopped = True
                vehicle.speed = 0
                queue_count += 1
            
            # Vertical vehicles approaching intersection
            elif vehicle.direction == 1 and vehicle.y > 80 and vehicle.y < 200:
                vehicle.stopped = True
                vehicle.speed = 0
                queue_count += 1
        
        # Green or yellow - vehicles can move
        else:
            if vehicle.stopped:
                vehicle.stopped = False
                vehicle.speed = vehicle.base_speed


def update_vehicles():
    """Update vehicle positions"""
    for vehicle in vehicles:
        if vehicle.direction == 0:  # Horizontal
            vehicle.x += vehicle.speed
            if vehicle.x > GRID_LENGTH + 100:
                vehicle.x = -GRID_LENGTH - 100
        else:  # Vertical
            vehicle.y += vehicle.speed
            if vehicle.y > GRID_LENGTH + 100:
                vehicle.y = -GRID_LENGTH - 100


def update_traffic_signal():
    """Update traffic signal timing - ONLY RUNS IN AUTOMATIC MODE"""
    global signal_timer, signal_state
    
    # Skip automatic updates if in manual mode
    if manual_mode:
        return
    
    signal_timer += 1
    
    if signal_state == 0:  # Red
        if signal_timer >= RED_TIME:
            signal_state = 1
            signal_timer = 0
    elif signal_state == 1:  # Yellow
        if signal_timer >= YELLOW_TIME:
            signal_state = 2
            signal_timer = 0
    elif signal_state == 2:  # Green
        if signal_timer >= GREEN_TIME:
            signal_state = 0
            signal_timer = 0


# ============================================================================
# MEMBER 1 - FEATURE 4: Dynamic Camera System
# ============================================================================
def setupCamera():
    """Configure camera with 3 modes: Bird's eye, Follow, Intersection"""
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 3000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Update for follow mode
    if camera_mode == 1:
        camera_pos[0] = vehicles[0].x - 300
        camera_pos[1] = vehicles[0].y - 300
        camera_pos[2] = 300
    
    x, y, z = camera_pos
    gluLookAt(x, y, z, 0, 0, 0, 0, 0, 1)


def keyboardListener(key, x, y):
    """Keyboard controls"""
    global is_night, is_highway, signal_state, signal_timer, manual_mode
    
    # Toggle night (N key)
    if key == b'n':
        is_night = not is_night
    
    # Toggle environment (E key)
    if key == b'e':
        is_highway = not is_highway
    
    # Manual signal control (T key) - FIXED VERSION
    if key == b't':
        manual_mode = True  # Enable manual mode
        signal_timer = 0  # Reset timer
        signal_state = (signal_state + 1) % 3  # Move to next state
    
    # Toggle automatic mode (A key) - NEW
    if key == b'a':
        manual_mode = not manual_mode
        if not manual_mode:
            signal_timer = 0  # Reset timer when returning to auto
    
    # Speed up (W key)
    if key == b'w':
        for v in vehicles:
            v.base_speed += 0.3
            v.speed = v.base_speed
    
    # Slow down (S key)
    if key == b's':
        for v in vehicles:
            v.base_speed = max(0.5, v.base_speed - 0.3)
            v.speed = v.base_speed
    
    # Reset (R key)
    if key == b'r':
        vehicles[0].x = -600
        vehicles[0].y = 60
        vehicles[1].x = -550
        vehicles[1].y = -60
        vehicles[2].x = 60
        vehicles[2].y = -600
        vehicles[3].x = -60
        vehicles[3].y = -550
        for v in vehicles:
            v.base_speed = 2.0
            v.speed = 2.0
            v.stopped = False
            v.warning = False


def specialKeyListener(key, x, y):
    """Arrow key controls for camera"""
    global camera_pos
    
    if key == GLUT_KEY_UP:
        camera_pos[2] += 20
    if key == GLUT_KEY_DOWN:
        camera_pos[2] = max(150, camera_pos[2] - 20)
    if key == GLUT_KEY_LEFT:
        camera_pos[0] -= 20
    if key == GLUT_KEY_RIGHT:
        camera_pos[0] += 20


def mouseListener(button, state, x, y):
    """Mouse click to toggle camera modes"""
    global camera_mode, camera_pos
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        camera_mode = (camera_mode + 1) % 3
        
        if camera_mode == 0:  # Bird's eye
            camera_pos = [0, 800, 800]
        elif camera_mode == 1:  # Follow
            camera_pos = [vehicles[0].x - 300, vehicles[0].y - 300, 300]
        elif camera_mode == 2:  # Intersection
            camera_pos = [400, 400, 300]


def idle():
    """Continuous update function"""
    update_vehicles()
    check_collisions()
    check_signal_stop()
    check_speed_boost()  # Check speed boost zones
    update_traffic_signal()  # Now respects manual_mode flag
    glutPostRedisplay()


def showScreen():
    """Main display function"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setupCamera()
    
    # Draw ground using GL_QUADS
    glBegin(GL_QUADS)
    if is_night:
        glColor3f(0.05, 0.1, 0.05)
    else:
        glColor3f(0.15, 0.5, 0.15)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, -1)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, -1)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, -1)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, -1)
    glEnd()
    
    # Draw all scene elements
    draw_roads()
    draw_speed_zones()  # Draw speed boost zones
    draw_traffic_signal()
    draw_street_lights()
    
    if is_highway:
        draw_highway_barriers()
    else:
        draw_city_buildings()
    
    # Draw all vehicles
    for vehicle in vehicles:
        glPushMatrix()
        glTranslatef(vehicle.x, vehicle.y, vehicle.z + 30)
        if vehicle.direction == 1:
            glRotatef(90, 0, 0, 1)
        draw_vehicle(vehicle.type, vehicle.warning)
        glPopMatrix()
    
    # Display UI information
    signal_names = ["RED", "YELLOW", "GREEN"]
    camera_names = ["Bird's Eye", "Follow Vehicle", "Intersection"]
    env_name = "HIGHWAY" if is_highway else "CITY"
    time_mode = "NIGHT" if is_night else "DAY"
    mode_text = "MANUAL" if manual_mode else "AUTO"
    
    avg_speed = sum(v.speed for v in vehicles) / len(vehicles)
    
    draw_text(10, 770, f"Signal: {signal_names[signal_state]} ({mode_text}) | Queue: {queue_count}")
    draw_text(10, 745, f"Camera: {camera_names[camera_mode]}")
    draw_text(10, 720, f"Environment: {env_name} | Time: {time_mode}")
    draw_text(10, 695, f"Average Speed: {avg_speed:.1f}")
    
    if boost_active:
        glColor3f(0, 1, 0)
        draw_text(350, 745, "*** SPEED BOOST ACTIVE ***")
    
    draw_text(10, 50, "Controls: [N] Night | [E] Environment | [T] Manual Signal | [A] Auto/Manual")
    draw_text(10, 25, "[W/S] Speed | [R] Reset | [Mouse] Camera | [Arrows] Move")
    
    if any(v.warning for v in vehicles):
        draw_text(350, 770, "*** COLLISION WARNING ***")
    
    glutSwapBuffers()


def main():
    """Initialize and start"""
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"3D Traffic Simulation System")
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()


if __name__ == "__main__":
    main()