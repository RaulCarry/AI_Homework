(define (problem level0)
  (:domain sokoban)
  (:objects
    up down left right - direction
    pos_1_1 pos_2_1 pos_3_1 pos_4_1 pos_5_1 - location
  )
  (:init
    (move-dir pos_1_1 pos_2_1 right)
    (move-dir pos_2_1 pos_1_1 left)
    (move-dir pos_2_1 pos_3_1 right)
    (move-dir pos_3_1 pos_2_1 left)
    (move-dir pos_3_1 pos_4_1 right)
    (move-dir pos_4_1 pos_3_1 left)
    (move-dir pos_4_1 pos_5_1 right)
    (move-dir pos_5_1 pos_4_1 left)
    (at-player pos_1_1)
    (at-box pos_5_1)
    (clear pos_2_1)
    (clear pos_3_1)
    (clear pos_4_1)
  )
  (:goal (and
    (at-box pos_3_1)
  ))
)