def valid_pos(start_position, end_position):
    if abs(end_position[0] - start_position[0]) == abs(end_position[1] - start_position[1]):
        return True
    else:
        return False




print(valid_pos([1,6],[4,4]))