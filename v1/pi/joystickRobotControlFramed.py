import pygame
import serial
from tendo import singleton

me = singleton.SingleInstance() # will sys.exit(-1) if another instance is running

# Define some colors
BLACK    = (   0,   0,   0)
WHITE    = ( 255, 255, 255)

# Init serial
ser = serial.Serial('/dev/ttyUSB0', 57600)
ser.write("A,0,000,0,000,S")

# Robot wheel speed
DIRECTION_FORWARD = '1'
DIRECTION_BACKWARD = '0'
leftWheelSpeed = 200
rightWheelSpeed = 200

def createFrame(leftDirection, _leftWheelSpeed, rightDirection, _rightWheelSpeed):
    frame = "A," + leftDirection + "," + format(_leftWheelSpeed, '03') + "," + rightDirection + "," + format(_rightWheelSpeed, '03') + ",S"
    return frame
def leftForwardSpeed(y):
    return y*237.5 + 17.5
def leftRot(x):
    return x*220
def rightForwardSpeed(y):
    return y*255
def rightRot(x):
    return x*(-255)
def combine(x,y,xvalue,yvalue):
    return int(abs(x)/(abs(x)+abs(y))*xvalue + abs(y)/(abs(x)+abs(y))*yvalue)
def rightSpeed(x,y):
    return combine(x,y,rightRot(x),rightForwardSpeed(y))
def leftSpeed(x,y):
    return combine(x,y,leftRot(x),leftForwardSpeed(y))
def createFrameSignedSpeeds(leftSpeed, rightSpeed):
    leftDir =  DIRECTION_FORWARD if (leftSpeed > 0) else DIRECTION_BACKWARD
    rightDir = DIRECTION_FORWARD if (rightSpeed > 0) else DIRECTION_BACKWARD
    return createFrame(leftDir, abs(leftSpeed), rightDir, abs(rightSpeed))


# This is a simple class that will help us print to the screen
# It has nothing to do with the joysticks, just outputing the
# information.
class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def printS(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, [self.x, self.y])
        self.y += self.line_height
        
    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15
        
    def indent(self):
        self.x += 10
        
    def unindent(self):
        self.x -= 10
    

pygame.init()
 
# Set the width and height of the screen [width,height]
size = [500, 700]
screen = pygame.display.set_mode(size)

pygame.display.set_caption("My Game")

#Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Initialize the joysticks
pygame.joystick.init()
    
# Get ready to print
textPrint = TextPrint()

# -------- Main Program Loop -----------
while done==False:
        
    # EVENT PROCESSING STEP
    for event in pygame.event.get(): # User did something
        if event.type == pygame.QUIT: # If user clicked close
            done=True # Flag that we are done so we exit this loop
        
        # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        if event.type == pygame.JOYBUTTONDOWN:
            joystick = pygame.joystick.Joystick(0)
            print("Joystick button pressed.")
            button0 = joystick.get_button(0)
            if (button0):
                leftWheelSpeed = leftWheelSpeed + 1
            button1 = joystick.get_button(1)
            if (button1):
                leftWheelSpeed = leftWheelSpeed - 1
            button2 = joystick.get_button(2)
            if (button2):
                rightWheelSpeed = rightWheelSpeed + 1
            button3 = joystick.get_button(3)
            if (button3):
                rightWheelSpeed = rightWheelSpeed - 1
            frame = (createFrame(DIRECTION_FORWARD, leftWheelSpeed, DIRECTION_FORWARD, rightWheelSpeed))
            print frame
        if event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")
            
    joystick = pygame.joystick.Joystick(0)
    
 
    # DRAWING STEP
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(WHITE)
    textPrint.reset()

    # Wait for serial
    #l = ser.readline()
    #textPrint.printS(screen, l)

    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()

    textPrint.printS(screen, "Number of joysticks: {}".format(joystick_count) )
    textPrint.indent()
    
    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        axis_x = joystick.get_axis(0)
        axis_y = -1*joystick.get_axis(1)
        if (abs(axis_x) > 0.125) or (abs(axis_y) > 0.125):
            frame = createFrameSignedSpeeds(leftSpeed(axis_x, axis_y),rightSpeed(axis_x, axis_y))
            #print frame
			#send frame to log server
			
            ser.write(frame)
    
        textPrint.printS(screen, "Joystick {}".format(i) )
        textPrint.indent()
    
        # Get the name from the OS for the controller/joystick
        name = joystick.get_name()
        textPrint.printS(screen, "Joystick name: {}".format(name) )
        
        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()
        textPrint.printS(screen, "Number of axes: {}".format(axes) )
        textPrint.indent()
        
        for i in range( axes ):
            axis = joystick.get_axis( i )
            textPrint.printS(screen, "Axis {} value: {:>6.3f}".format(i, axis) )
        textPrint.unindent()
            
        buttons = joystick.get_numbuttons()
        textPrint.printS(screen, "Number of buttons: {}".format(buttons) )
        textPrint.indent()

        for i in range( buttons ):
            button = joystick.get_button( i )
            textPrint.printS(screen, "Button {:>2} value: {}".format(i,button) )
        textPrint.unindent()

        
            
            
        # Hat switch. All or nothing for direction, not like joysticks.
        # Value comes back in an array.
        hats = joystick.get_numhats()
        textPrint.printS(screen, "Number of hats: {}".format(hats) )
        textPrint.indent()

        for i in range( hats ):
            hat = joystick.get_hat( i )
            textPrint.printS(screen, "Hat {} value: {}".format(i, str(hat)) )
            x = hat[0]
            y = hat[1]
            if (y == 1) :
                frame = (createFrame(DIRECTION_FORWARD, leftWheelSpeed, DIRECTION_FORWARD, rightWheelSpeed))
            elif (x == 1) :
                frame = (createFrame(DIRECTION_FORWARD, leftWheelSpeed, DIRECTION_BACKWARD, rightWheelSpeed))
            elif (y == -1) :
                frame = (createFrame(DIRECTION_BACKWARD, leftWheelSpeed, DIRECTION_BACKWARD, rightWheelSpeed))
            elif (x == -1) :
                frame = (createFrame(DIRECTION_BACKWARD, leftWheelSpeed, DIRECTION_FORWARD, rightWheelSpeed))
            else :
                frame = ""
            ser.write(frame)
            
        textPrint.unindent()
        
        textPrint.unindent()

    
    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
    
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()

    # Limit to 20 frames per second
    clock.tick(20)
    
# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit ()
