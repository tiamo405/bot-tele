import datetime

def chuyen_doi_Am_Pm(hour) :
    meridiem = None
    if hour <=12 :
        meridiem ="AM"
    else :
        hour -= 12
        meridiem ='PM'
    return hour, meridiem
def get_time():
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute
    return hour, minute

def add_time(hour, minute, delta) :
    delta = datetime.timedelta(minutes=delta)
    time = datetime.time(hour= hour, minute= minute)
    new_time = (datetime.datetime.min + datetime.timedelta(hours=time.hour, \
                minutes=time.minute) + delta).time()
    new_hour, new_minute= new_time.hour, new_time.minute
    return new_hour, new_minute

def sleep_times(hour = None, minute = None, chuki = 5, check = True) : # input hour, minute, output: 5 chu ki ngu, 1 chu ki 90 phut
    if check :
        hour, minute = get_time()
    delta = datetime.timedelta(minutes=90)
    new_hour = []
    new_minute = []
    new_meridiem = []
    new_hour_meridiem = []
    new_minute.append(minute)
    new_hour.append(hour)
    hour, minute= add_time(hour= hour, minute= minute, delta= 14)
    new_minute.append(minute)
    new_hour.append(hour)
    for i in range(chuki):
        # time = datetime.time(hour= new_hour[-1], minute= new_minute[-1])    
        # new_time = (datetime.datetime.min + datetime.timedelta(hours=time.hour, minutes=time.minute) + delta).time()
        hour, minute = add_time(new_hour[-1], new_minute[-1], delta= 90) 
        new_hour.append(hour)
        new_minute.append(minute)
    
    for i in range(len(new_hour)):
        h,mer = chuyen_doi_Am_Pm(new_hour[i])
        new_hour_meridiem.append(h)
        new_meridiem.append(mer)
    return new_hour_meridiem, new_minute, new_meridiem

def message_sleep_now(hours, minutes, meridiems) :
    txt = 'Bây giờ là {}:{} {}. Nếu bạn đi ngủ ngay bây giờ, bạn nên cố gắng thức dậy vào một trong những thời điểm sau: \n \
        ⏰ {}:{} {} cho một chu kỳ - ngủ một tiếng rưỡi.\n \
        ⏰ {}:{} {} cho hai chu kỳ - ngủ ba tiếng.\n \
        ⏰ {}:{} {} cho ba chu kỳ - ngủ bốn tiếng rưỡi.\n \
        ⏰ {}:{} {} cho bốn chu kỳ - ngủ sáu tiếng.\n \
        ⏰ {}:{} {} cho năm chu kỳ - ngủ bảy tiếng rưỡi.\n \
        Xin lưu ý rằng bạn nên đi ngủ vào những thời điểm này. Con người trung bình mất ~14 phút để đi vào giấc ngủ, vì vậy hãy lên kế hoạch cho phù hợp! \n \
        \n Chúc ngủ ngon! 😴'.format(hours[0], minutes[0], meridiems[0],\
                                    # hours[1], minutes[1], meridiems[1],\
                                    hours[2], minutes[2], meridiems[2],\
                                    hours[3], minutes[3], meridiems[3],\
                                    hours[4], minutes[4], meridiems[4],\
                                    hours[5], minutes[5], meridiems[5],\
                                    hours[6], minutes[6], meridiems[6]    )
    return txt

# new_hour_meridiem, new_minute, new_meridiem = sleep_times()
# print(message_sleep_now(hours= new_hour_meridiem, minutes= new_minute, meridiems= new_meridiem))