# Pen Plotter

## Overview

The goal of this project was to create a pen plotter with 2.5 degrees of freedom. That is, a pen plotter capable of drawing on 
a 2D plane (2 degrees of freedom) with an additional pen-up and pen-down movement (half a degree of freedom). This design was 
a compact two arm linkage which was actuated by two stepper motors and a scissor lift.

The video demo of the project can be seen [here](https://drive.google.com/file/d/1AHaPgYhn4Wa2hROuMRt8auDsZj5_-b34/view?usp=sharing)

### Hardware Overview

As shown in Figure 1, the plotter uses a two arm linkage and two stepper motors to plot in the xy-plane. 
***ADD MORE TO THIS SECTION***
- TMC4210
- Stepper motors

### Software Overview

The pen plotter makes use of a cooperative multitaking architecture to process and plot images. Drawings are uploaded as HPGL files, 
which are processed by the device to actuate the motors. There are two methods that are used to actuate the drawing of the plotter: 
interpolation and the Newton-Raphson root finding algorithm.

Interpolation is used to draw straight lines. Since both stepper motors will not turn at the same speed, it is likely that straight lines
will become curved. To remedy this, interpolation is used to break long distances in between coordinates up into smaller steps so that 
the motors will be able to move together.

Next is the algorithm to find the desired angles of the motors. HPGL files designate an xy-coordinate, but the plotter is actuated by two
angles that create an xy-coordinate. Finding these angles is a matter of inverse kinematics, which are implemented using the Newton-Raphson
root finding algorithm. Given a desired x and y coordinate pair, the algorithm determines which angle each motor should be at to move the 
pen to the desired location.

![](https://github.com/alaurin10/ME405/blob/main/docs/structure.jpg)
Figure 1: Pen Plotter

## Hardware Design and Considerations

Originally, our design would raise and lower the entire plotter with the pen attached to allow for multiple lines while drawing. Since the pen is attached at the end of a slender plastic rod, it was unfeasible to attach a mechanism that would only lift the pen. Instead, a DC motor would be attached at the base of the plotter and rotate a cam that would lift the plotter along a rod. Our original cam design caused problems, however, as we found that the motor needed to spin at nearly 100% to go from the down position to the up position, and the up position was at such a small range of the cam, that even by using encoders, after three or four cycles of up/down, the cam orientation would be off, and the plotter would not be able to rise. Our second cam design made use of an ellipse, hoping to allow for smoother transition between the up and down motions, but the motor was unable to provide enough torque, even at max speed, to lift the plotter. 


### Bill of Materials

| Qty. | Part                 | Vendor           | Est. Price  |
| :--: | :-----------:        | :-------------:  | :---------: |
| 2    | ME405 Stepper Motors | ME405 Class      | - |
| 1  | Nucleo Board with Shoe| ME405 Class | - |
| 2 | Jutagoss Motor GA12-N20 DC Gear Motor | Amazon | $27.38 |
| 1 | Pen | Team Member | - |
| 1 | PLA 3D Filament | Team Member | - |
| 8 | M3-8mm Screws | School Shop | - |
| 2 | KHK-BSS0.5-60B Gears | khk.gears.us | $20.75 |
| 3 | 1601 Series Flanged Ball Bearing | Servo City | $6.38 |
| 2 | 5mm Stainless Steel Shafting | Servo City | $2.88 |
| 8 | M4 x 17mm Screws | Team Member | - |
| 4 | M4 x 10mm Screws | Team Member | - |
| 1 | Guide Rails System | Team Member | - |
| 1 | Platform | Team Member | - |
| 1 | 3D Printed Base | Team Member | - |
| 1 | 3D Printed Arm | Team Member | - |
| 1 | Raspberry Pi Pico | Team Member | - |
| 1 | NeoPixel RGBW Flex Strip | Team Member | - |
| 1 | MAX98357A | Team Member | - |
| 1 | Speaker | Team Member | - |

## Software Design and Considerations


## Results

