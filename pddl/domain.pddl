(define (domain sokoban)
  (:requirements :typing :strips)
  (:types location direction)
  
  (:predicates
    (at-player ?l - location)                  
    (at-box ?l - location)                     
    (clear ?l - location)                      
    (move-dir ?from ?to - location ?d - direction)
    (is-goal ?l - location)               
  )

  (:action move
    :parameters (?from ?to - location ?d - direction)
    :precondition (and 
        (at-player ?from)
        (clear ?to)
        (move-dir ?from ?to ?d)
    )
    :effect (and 
        (not (at-player ?from))
        (at-player ?to)
        (clear ?from)
        (not (clear ?to))
    )
  )

  (:action push
    :parameters (?player-loc ?box-loc ?to-loc - location ?d - direction)
    :precondition (and 
        (at-player ?player-loc)
        (at-box ?box-loc)
        (clear ?to-loc)
        (move-dir ?player-loc ?box-loc ?d)
        (move-dir ?box-loc ?to-loc ?d)
    )
    :effect (and 
        (not (at-player ?player-loc))
        (not (at-box ?box-loc))
        (not (clear ?to-loc))
        (at-player ?box-loc)
        (at-box ?to-loc)
        (clear ?player-loc)
    )
  )
)