from app import manager

@manager.command
def init(): 
    print 'OK'

if __name__ == '__main__':
    manager.run()
