# coding: utf-8

"""命令行火车票查看器

Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h,--help   显示帮助菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达


"""
from docopt import docopt
from stations import stations
import requests
import re
from prettytable import PrettyTable

class TrainsCollection():
    header='车次 车站 时间 历时 特等 一等 二等 高软 软卧 动卧 硬卧 软座 硬座 无座 其他'.split()
    def __init__(self,available_trains,options):
        """trains set got after query

        :param available_trains: a dic with (key ,value)=(train_index , site_info )
        :param options: trains' type ,such as gaotie ,dongche ...etc
        """
        self.available_trains=available_trains
        self.options=options

    def _get_duration(self,raw_train):
        duration = raw_train.get('dur').replace(':', '小时') + '分'
        if duration.startswith('00'):
            return duration[4:]
        if duration.startswith('0'):
            return duration[1:]
        return duration

    @property
    def trains(self):
        for raw_train in self.available_trains:
            train_no = raw_train['index']
            initial = train_no[0].lower()
            if not self.options or initial in self.options:
                train = [
                    train_no,
                    '\n'.join([raw_train['loc'][0],
                               raw_train['loc'][1]]),
                    '\n'.join([raw_train['time'][0],
                               raw_train['time'][1]]),
                    self._get_duration(raw_train),
                    raw_train['rank'][0],
                    raw_train['rank'][1],
                    raw_train['rank'][2],
                    raw_train['rank'][3],
                    raw_train['rank'][4],
                    raw_train['rank'][5],
                    raw_train['rank'][6],
                    raw_train['rank'][7],
                    raw_train['rank'][8],
                    raw_train['rank'][9],
                    raw_train['rank'][10]
                ]
                yield train

    def pretty_print(self):
        pt = PrettyTable()
        pt._set_field_names(self.header)
        for train in self.trains:
            pt.add_row(train)
        print(pt)


def wash(split_item):
    time = (split_item[7], split_item[8])
    durtime = split_item[9]
    location = (split_item[3], split_item[4])
    site_type = split_item[18:31]
    site_type.reverse()
    train_index = split_item[2]
    info={'index':train_index,'time':time,'dur':durtime,'loc':location,'rank':site_type}
    return info


def cli():
    """command-line interface"""
    ##########
    #Parse arguments
    ##########
    arguments = docopt(__doc__)
    from_station=stations.get(arguments['<from>'])
    to_station=stations.get(arguments['<to>'])
    date=arguments['<date>']
    options = ''.join([
        key for key, value in arguments.items() if value is True
    ])


    url='https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'\
        .format(date,from_station,to_station)
    response = requests.get(url,verify=False)


    ################
    #wash dirty response
    ###############
    #raw_data=[train1 , train 2,.....]
    #where train1 is a list of information ,due to the website's chaos ,i had to wash the response later
    ################

    raw_data=response.json()['data']['result']
    split_items=[re.split('\|',train) for train in raw_data]
    print(split_items[0])
    split_items=[item.pop(0) for item in split_items]
    split_items=[item.pop(11) for item in split_items]
    available_trains=[wash(item) for item in split_items]

    ############
    #print outcome
    ############
    TrainsCollection(available_trains, options).pretty_print()




if __name__ == '__main__':
    cli()