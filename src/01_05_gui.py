import sys, pygame
import time, numpy as np
import configparser

save_flag = True
align_flag=True

# constants
size = width, height = 640, 600
speed = [0, -1]
black = 0, 0, 0
white = 255, 255, 255
border = 0, 0, 0
text_color = 255, 0, 0

# 讀取 config.ini
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf8')
purchase_station_count = int(config['DEFAULT']['售票口個數']) #int(input("售票口個數: "))
checking_station_count = int(config['DEFAULT']['驗票口個數']) #int(input("驗票口個數: "))
store_count = int(config['DEFAULT']['小吃部銷售員人數']) #int(input("小吃部銷售員人數: "))

person_size = (20, 20)
station_size = (50, 50)
offset = 10 # store distance
play_speed = 60  # 60 frames per second

class Person(pygame.sprite.Sprite):
    def __init__(self, screen, no, status):
        # Call the parent class (Sprite) constructor
        super().__init__()

        image = pygame.image.load("svg/person.svg")
        image = pygame.transform.scale(image, person_size)
        self.image = image
        self.rect = image.get_rect()
        self.no = no
        self.original_position = self.position = [self.rect.x, self.rect.y] = [20, int(height/2)]
        screen.blit(image, self.rect)
        # if self.no < 1 : print('0:', self.original_position)
    def display(self):
        # if self.move_step >= total_move_step or self.move_step >= self.service_time:
            # self.rect.x, self.rect.y = self.position[0], self.position[1]
            # print('last:', self.original_position)
        # else:
            # self.rect.x, self.rect.y = self.get_middle_position(self.position)
            # self.move_step += 1
            
        if self.move_step <= self.service_time and self.service_time > 0:
            self.move_step += 1
            self.rect.x, self.rect.y = self.get_middle_position(self.position)
        elif self.service_time == 0:
            self.rect.x, self.rect.y = self.position[0], self.position[1]

    def display_align(self, position):
        self.position = position
        self.rect.x, self.rect.y = self.position[0], self.position[1]
        
    def get_middle_position(self, position):
        x = self.original_position[0] + int((position[0] - self.original_position[0]) * self.move_step / self.service_time)
        y = self.original_position[1] + int((position[1] - self.original_position[1]) * self.move_step / self.service_time)
        return x, y
        
    def change_status(self, status, position, service_time):
        self.status = status
        self.move_step = 0
        self.service_time = service_time
        self.original_position = self.position
        self.position = position
        # print(self.original_position, self.position)

    # def move(self, screen, position):
        # self.rect = self.rect.move(position)
        # screen.blit(self.image, self.rect)

class Station():
    def __init__(self, image_file, position):
        image = pygame.image.load(f"svg/{image_file}.svg")
        image = pygame.transform.scale(image, station_size)
        rect = image.get_rect()
        self.rect = rect
        self.rect.x, self.rect.y = position[0], position[1]
        self.image = image
        # print(image_file, ":", self.rect.x, self.rect.y)
    def display(self, screen):
        screen.blit(self.image, self.rect)
    
def parse_log(no):
    list = log_rows[no].split(',')   
    return float(list[0]) * 60, int(list[1]), list[2], float(list[3][:-1]) * 60

def calculate_purchase_station_position(i):
    x = int(width/4)
    y = station_size[0] + offset + int((i*(height-20)/(purchase_station_count+1)))
    return [x, y]

def calculate_checking_station_position(i):
    x = int(width*2/3)
    y = int(height*2/3) - station_size[0] - 30
    return [x, y]

def calculate_store_position(i):
    return [int(width*2/3)+(i-2)*(station_size[0] + offset), station_size[0]]

def calculate_seat_position():
    x = int(width*1/3)+30
    y = int(height*2/3)
    return [x, y, width*3/5, height-y-20]

def calculate_purchase_station_queue_position(i):
    queue_length, queue_no = divmod(i, purchase_station_count)
    # queue_no -= 1
    [x, y] = calculate_purchase_station_position(queue_no)

    x -= (queue_length+1)*20
    return [x, y+station_size[0]]

def calculate_checking_station_queue_position(i):
    queue_length, queue_no = divmod(i, checking_station_count)
    # queue_no -= 1
    [x, y] = calculate_checking_station_position(queue_no)

    x -= (queue_length+1)*20
    return [x, y+station_size[0]]

def calculate_store_queue_position(i):
    queue_length, queue_no = divmod(i, store_count)
    # queue_no -= 1
    [x, y] = calculate_store_position(queue_no)

    if queue_length < 9:
        y += (queue_length+1)*20
    else:
        y += ((queue_length%9)+1)*20
        x += int(station_size[0]*0.5)
    
    return [x, y+station_size[0]]

def calculate_seat_queue_position(i):
    queue_length, queue_no = divmod(i, 18)
    [x, y, _, _] = calculate_seat_position()
    y += (queue_length)*(person_size[0]+5) + 5
    return [x+10+queue_no*person_size[0], y]

def display_text(screen, content, x, y):
    font = pygame.font.Font("c:/windows/fonts/msjh.ttc", 24)
    text = font.render(content, True, text_color)
    textRect = text.get_rect()
    textRect.center = (x, y)
    screen.blit(text, textRect)

# main
log_file = open('./record.log', 'r', encoding='utf8')
log_rows = log_file.readlines()


pygame.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption('售票流程模擬視覺化')

all_sprites_list = pygame.sprite.Group()

# resource list
purchase_station_list = []
for i in range(purchase_station_count):
    purchase_station_list.append(Station('tv', calculate_purchase_station_position(i)))
checking_station_list = []
for i in range(checking_station_count):
    checking_station_list.append(Station('passport', calculate_checking_station_position(i)))
store_list = []
for i in range(store_count):
    store_list.append(Station('store', calculate_store_position(i)))

# initialize queues
purchase_station_queue = []
checking_station_queue = []
store_queue = []
seat_queue = []

# read log and visualize
current_time = 0  
no = 0
next_time, moviegoer, status, service_time = parse_log(no)
 
clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    # background
    screen.fill(white)
    # Drawing Rectangle
    pygame.draw.rect(screen, border, (0, 0, width, height), 5)
    pygame.draw.rect(screen, black, calculate_seat_position(), 2)

    # fixed resources
    for purchase_station in purchase_station_list:
        purchase_station.display(screen)
    for checking_station in checking_station_list:
        checking_station.display(screen)
    for store in store_list:
        store.display(screen)
        
    # display text
    [x, y] = calculate_purchase_station_position(0)
    display_text(screen, '售票口', x+30, y-20)
    [x, y] = calculate_checking_station_queue_position(0)
    display_text(screen, '驗票口', x+110, y-20)
    [x, y] = calculate_store_position(0)
    display_text(screen, '小吃部', x+150, y-30)

    if next_time <= current_time:
        if status == 'arrival':
            person = Person(screen, moviegoer, status)
            purchase_station_queue.append(person)
            position = calculate_purchase_station_queue_position(len(purchase_station_queue))
            person.change_status(status, position, service_time)
            all_sprites_list.add(person)
        elif status == 'purchase_ticket':
            person = purchase_station_queue.pop(0)
            position = calculate_checking_station_queue_position(len(checking_station_queue))
            person.change_status(status, position, service_time)
            checking_station_queue.append(person)
        elif status == 'check_ticket_store_in':
            person = checking_station_queue.pop(0)
            position = calculate_store_queue_position(len(store_queue))
            person.change_status(status, position, service_time)
            store_queue.append(person)
        elif status == 'store_out':
            person = store_queue.pop(0)
            position = calculate_seat_queue_position(len(seat_queue))
            person.change_status(status, position, service_time)
            seat_queue.append(person)
        elif status == 'check_ticket_wo_food':
            person = checking_station_queue.pop(0)
            position = calculate_seat_queue_position(len(seat_queue))
            person.change_status(status, position, service_time)
            seat_queue.append(person)

        # print(len(purchase_station_queue), len(checking_station_queue), len(store_queue), len(seat_queue))

        no += 1
        if no < len(log_rows): 
            next_time, moviegoer, status, service_time = parse_log(no) 
        else:   
            next_time = np.inf
            if align_flag:
                for i, person in enumerate(seat_queue):
                    person.display_align(calculate_seat_queue_position(i))
                align_flag=False
            time.sleep(10)
            break


    # display persons，重算每個人的排隊位置
    # for i, person in enumerate(purchase_station_queue):
        # person.display_align(calculate_purchase_station_queue_position(i))
    # for i, person in enumerate(checking_station_queue):
        # person.display_align(calculate_checking_station_queue_position(i))
    # for i, person in enumerate(store_queue):
        # person.display_align(calculate_store_queue_position(i))
    # for i, person in enumerate(seat_queue):
        # person.display_align(calculate_seat_queue_position(i))

    # 另一種作法 person.display()，依據每個人的排隊位置移動，排列會不整齊
    for i, person in enumerate(purchase_station_queue):
        person.display() # calculate_purchase_station_queue_position(i))
    for i, person in enumerate(checking_station_queue):
        person.display() # calculate_checking_station_queue_position(i))
    for i, person in enumerate(store_queue):
        person.display() # calculate_store_queue_position(i))
    for i, person in enumerate(seat_queue):
        person.display() # calculate_seat_queue_position(i))
        
    # 每隔一陣子重新排列小吃部，使小吃部排列整齊
    if (current_time+1)%10==0: 
        for i, person in enumerate(store_queue):
            person.display_align(calculate_store_queue_position(i))
            
    # 更新畫面
    all_sprites_list.update()
    all_sprites_list.draw(screen)
    pygame.display.flip()
            
    if save_flag:   
        if (current_time+1)%10==1: 
            pygame.image.save(screen, f"screenshot/{current_time//10:4d}.png")
    
    clock.tick(play_speed)
    current_time+=1
    
pygame.quit()