import os
import cv2
import glob
import collections
import dataclasses
import argparse

def error(*args, **kwargs):
    print('[ERROR]', *args, **kwargs)

def log(*args, **kwargs):
    print('[LOG]', *args, **kwargs)

def get_label_path_replace(image_path):
    position = image_path.rfind('.')
    label_path = image_path[:position] + '.txt'

    return label_path

def get_label_path_add(image_path):
    label_path = image_path + '.txt'
    return label_path

Label = collections.namedtuple('Label', 'name x1 y1 x2 y2')
def make_label_parser(separator):
    'separator를 이용한 label_parser 함수를 생성'
    def inner_function(label_path):
        labels = []
        with open(label_path, 'rt') as istream:
            for line in istream.readlines():
                try:
                    line = line.split(separator)
                    name = line[4]
                    x1   = int(line[0])
                    y1   = int(line[1])
                    x2   = int(line[2])
                    y2   = int(line[3])
                except:
                    error('29-34 line의 코드를 각 코드의 저장방법에 맞게 간단히 수정할 필요가 있습니다.')
                    exit(2)

                labels.append(Label(name, x1, y1, x2, y2))
        return labels
    return inner_function

@dataclasses.dataclass
class COLOR:
    RED      = (255, 0, 0)
    BLUE     = (0, 0, 255)
    BLACK    = (0, 0, 0)

def main():
    parser = argparse.ArgumentParser(description='simple verification code for labeling')
    parser.add_argument('-d', '--directory',
                        required=True,
                        help='Enter image and label directory')

    parser.add_argument('-lt', '--label_type',
                        default='replace',
                        choices=('replace', 'add'),
                        help='Enter the navigation method for the label file')
                        
    parser.add_argument('-s', '--separator',
                        default=',',
                        help='Enter the separator for the label file')

    
    args = parser.parse_args()

    log('[ Start ]')

    # 디렉터리 존재 여부 검증
    if os.path.exists(args.directory):
        if os.path.isdir(args.directory):
            pass
        else:
            error(f'<{args.directory}> isn\'t directory, please check again')
            exit(1)
    else:
        error(f'<{args.directory}> doesn\'t exist, please check again')
        exit(1)

    log('Directory: ', args.directory)

    # 라벨 파일 
    if args.label_type == 'replace':
        get_label_path = get_label_path_replace
    else:
        get_label_path = get_label_path_add
    
    # 라벨 파일 파서
    parse_label = make_label_parser(args.separator)
    
    images_path_list = []
    for extention in ('*.png', '*.jpg', '*.jpeg'):
        images_path_list.extend(glob.glob(os.path.join(args.directory, extention)))

    for image_path in images_path_list:
        label_path = get_label_path(image_path)
        
        if not (os.path.exists(label_path) and os.path.isfile(label_path)):
            log(os.path.split(image_path)[1], '...     pass')
            continue
        else:
            log(os.path.split(image_path)[1], '...     show')

        labels = parse_label(label_path)

        image = cv2.imread(image_path)
        for label in labels:
            name = label.name.strip().lower()
            if name == 'dog':
                color = COLOR.RED
            elif name == 'cat':
                color = COLOR.BLUE
            else:
                color = COLOR.BLACK

            cv2.rectangle(image, (label.x1, label.y1), (label.x2, label.y2), color)
            cv2.putText(image, name, (label.x1, label.y1), cv2.FONT_HERSHEY_SIMPLEX, 1, color)

        cv2.imshow('Image', image)
        cv2.waitKey()


    cv2.destroyAllWindows()
    log('[ End ]')


    

if __name__ == '__main__':
    main()