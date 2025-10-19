def search(number: id, numbers: list) -> bool:
    left, right = 0, len(numbers) - 1
    while left <= right:
        mid = (left + right) // 2
        if number > numbers[mid]:
            left = mid + 1
        elif number < numbers[mid]:
            right = mid - 1
        else:
            return True
    return False
