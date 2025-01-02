from pathlib import Path
import glob
import sqlite3
import shutil
import sys

import scrap    # scrap.py 파일 내부의 함수 사용

input = sys.stdin.readline


def fileManage():
    # 현재 디렉터리 체크
    cwd = Path.cwd()
    dataPath = Path.joinpath(cwd, "musicData.db")

    # musicData.db 파일이 존재하는지 체크 및 내용 갱신
    if dataPath.exists() == False:
        print("musicData.db 파일이 존재하지 않으므로 새로 생성합니다.", flush=True)
        if scrap.main() == True:
            print("파일 생성 완료")
        else:
            print("파일 생성 실패")
            return
    else:
        print("musicData.db 파일이 이미 존재합니다.", flush=True)
        print("musicData.db 파일을 갱신하시겠습니까? (Y/N) :", end=' ', flush=True)
        curInput = input().rstrip()
        if curInput in ['Y', 'y']:
            if scrap.main() == True:
                print("갱신 성공")
            else:
                print("갱신 실패")
                return
        elif curInput not in ['N', 'n']:
            print("유효하지 않은 조작")
            return

    # 정리해야 할 노래들이 있는 폴더의 데이터 반환
    print("정리해야 할 노래들이 있는 폴더의 이름을 적어주세요 :", end=' ', flush=True)
    beforeFolderPath = Path.joinpath(cwd, input().rstrip())
    if beforeFolderPath.exists() == True:
        mp3PathList = glob.glob(f'{beforeFolderPath}/*.mp3')
        mp3List = [Path(f).name for f in mp3PathList]
    else:
        print("폴더가 존재하지 않음")
        return

    # 정렬한 파일들을 저장할 Sort 폴더 체크  
    sortFolder = Path.joinpath(cwd, "Sort")
    if not sortFolder.exists():
        print("Sort 폴더가 존재하지 않으므로 새로 생성합니다.")
        sortFolder.mkdir(parents=True, exist_ok=True)

    # mp3List에 있는 모든 파일들에 대해 정리
    conn = sqlite3.connect('musicData.db')
    cursor = conn.cursor()
    for i in range(len(mp3List)):
        curMp3FileName = mp3List[i]
        cursor.execute('SELECT brand, genre FROM songs where fileName = ?', (curMp3FileName, ))
        result = cursor.fetchone()
        if result:
            brand, genre = result
            
            # brand 및 genre 폴더 경로 생성
            brandPath = sortFolder / brand
            genrePath = brandPath / genre
            brandPath.mkdir(parents=True, exist_ok=True)
            genrePath.mkdir(parents=True, exist_ok=True)

            # 파일 이동
            source = beforeFolderPath / curMp3FileName
            destination = genrePath / curMp3FileName
            shutil.move(str(source), str(destination))
        else:
            print(f'{curMp3FileName}는 데이터베이스에 없는 노래입니다.')

    conn.close()


fileManage()