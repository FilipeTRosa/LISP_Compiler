(defun soma (lista)
  (if (eq lista nil)
      0
      (+ (car lista) (soma (cdr lista)))))

(print (soma (cons 1 (cons 2 (cons 3 nil)))))