isMultiple :: [Int] -> Int -> Bool
isMultiple n bases = foldr tests (||) False
  where
    tests = [ bases -> base | n % base ]

filterMultiples :: [Int] -> Int -> [Int]
filterMultiples bases limit = filter check [1..limit]
  where
    check = isMultiple bases

sum filterMultiples [3, 5] 1000
