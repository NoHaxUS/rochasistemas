def is_excluded_cotation(cotation_name, kind):

    is_excluded = False

    if kind.pk == 38:
        excluded_cotations = [
            'Acima 0.5',
            'Acima 1.5',
            'Acima 2.5',
            'Acima 3.5',
            'Acima 4.5',
            'Acima 5.5',
            'Abaixo 0.5',
            'Abaixo 1.5',
            'Abaixo 2.5',
            'Abaixo 3.5',
            'Abaixo 4.5',
            'Abaixo 5.5',
        ]

        if not cotation_name in excluded_cotations:
            is_excluded = True

    elif kind.pk == 12:
        excluded_cotations = [
            'Acima 0.5',
            'Acima 1.5',
            'Acima 2.5',
            'Acima 3.5',
            'Acima 4.5',
            'Acima 5.5',
            'Abaixo 0.5',
            'Abaixo 1.5',
            'Abaixo 2.5',
            'Abaixo 3.5',
            'Abaixo 4.5',
            'Abaixo 5.5',
        ]
        
        if not cotation_name in excluded_cotations:
            is_excluded = True

    elif kind.pk == 976204:
        excluded_cotations = [
            'Acima 0.5',
            'Acima 1.5',
            'Acima 2.5',
            'Acima 3.5',
            'Acima 4.5',
            'Acima 5.5',
            'Abaixo 0.5',
            'Abaixo 1.5',
            'Abaixo 2.5',
            'Abaixo 3.5',
            'Abaixo 4.5',
            'Abaixo 5.5',
        ]

        if not cotation_name in excluded_cotations:
            is_excluded = True

    elif kind.pk == 976198:
        excluded_cotations = [
            'Acima 0.5',
            'Acima 1.5',
            'Acima 2.5',
            'Acima 3.5',
            'Acima 4.5',
            'Acima 5.5',
            'Abaixo 0.5',
            'Abaixo 1.5',
            'Abaixo 2.5',
            'Abaixo 3.5',
            'Abaixo 4.5',
            'Abaixo 5.5',
        ]
        
        if not cotation_name in excluded_cotations:
            is_excluded = True

    elif kind.pk == 47:
        excluded_cotations = [
            'Acima 0.5',
            'Acima 1.5',
            'Acima 2.5',
            'Acima 3.5',
            'Acima 4.5',
            'Acima 5.5',
            'Abaixo 0.5',
            'Abaixo 1.5',
            'Abaixo 2.5',
            'Abaixo 3.5',
            'Abaixo 4.5',
            'Abaixo 5.5',
        ]

        if not cotation_name in excluded_cotations:
            is_excluded = True


    #elif kind.pk == 63:
    #    is_excluded = True

    
    return is_excluded
