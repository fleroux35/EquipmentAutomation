import thorlabs_apt as apt
import time
#testfile for K10CR1
#All moves must be blocking or they will crash

if __name__ == "__main__":
    
    stage = apt.Motor(55113014)
    
    stage.enable()
    
    #There's a problem with default values on the unit, all need to be rounded
    stage.set_move_home_parameters(2,1,10,4)
    
    print(stage.get_velocity_parameters())
    
    stage.set_velocity_parameters(0,10,10)
        
    stage.move_home(True)
    
    print(stage.position)
    
    stage.move_to(80,True)    
    
    print(stage.position)
    
    stage.disable()
    
