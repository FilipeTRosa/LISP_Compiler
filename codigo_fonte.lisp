    (defun soma (lista)
      (if (eq lista nil) 0
        (+ (car lista) (soma (cdr lista)))))