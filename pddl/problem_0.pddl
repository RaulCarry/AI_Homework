(define (problem level0)
  (:domain sokoban)
  (:objects
    up down left right - direction
    pos_1_1 pos_2_1 pos_3_1 pos_4_1 pos_5_1 - location
  )
  (:init
    (adjacent pos_1_1 pos_2_1 right)
    (adjacent pos_2_1 pos_1_1 left)
    (adjacent pos_2_1 pos_3_1 right)
    (adjacent pos_3_1 pos_2_1 left)
    (adjacent pos_3_1 pos_4_1 right)
    (adjacent pos_4_1 pos_3_1 left)
    (adjacent pos_4_1 pos_5_1 right)
    (adjacent pos_5_1 pos_4_1 left)
    (at-player pos_1_1)
    (at-box pos_4_1)
    (clear pos_1_1)
    (clear pos_2_1)
    (clear pos_3_1)
    (clear pos_5_1)
  )
  (:goal (and
    (at-box pos_5_1)
  ))
)