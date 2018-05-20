def is_excluded_cotation(cotation_name, kind):

    is_excluded = False

    if kind.pk == 38:
        excluded_cotations = [
            'Acima 0.5',
            'Abaixo 2.5',
            'Abaixo 3.5',
            'Abaixo 4.5',
            'Abaixo 5.5',
            'Abaixo 3.0',
            'Abaixo 4.0',
            'Abaixo 5.0',
        ]

        if cotation_name in excluded_cotations:
            is_excluded = True

    elif kind.pk == 12:
        excluded_cotations = [
            'Acima 0.5', 
            'Abaixo 4.5',
            'Abaixo 5.5',
            'Abaixo 6.5',
            'Abaixo 7.5',
            'Abaixo 8.5',
            'Abaixo 9.5',
            'Abaixo 4.0',
            'Abaixo 5.0',
            'Abaixo 6.0',
            'Abaixo 7.0',
            'Abaixo 8.0',
            'Abaixo 9.0',
            'Abaixo 4.75',
            'Abaixo 5.75',
            'Abaixo 6.75',
            'Abaixo 7.75',
            'Abaixo 8.75',
            'Abaixo 9.75',
        ]
        
        if cotation_name in excluded_cotations:
            is_excluded = True

    elif kind.pk == 976204:
        excluded_cotations = [
            'Abaixo 2.0',
            'Abaixo 3.0',
            'Abaixo 4.0',
            'Abaixo 5.0',
            'Abaixo 2.5',
            'Abaixo 3.5',
            'Abaixo 4.5',
            'Abaixo 5.5',
        ]

        if cotation_name in excluded_cotations:
            is_excluded = True

    elif kind.pk == 976198:
        excluded_cotations = [
            'Abaixo 2.0',
            'Abaixo 3.0',
            'Abaixo 4.0',
            'Abaixo 5.0',
            'Abaixo 2.5',
            'Abaixo 3.5',
            'Abaixo 4.5',
            'Abaixo 5.5',
        ]
        
        if cotation_name in excluded_cotations:
            is_excluded = True

    elif kind.pk == 47:
        excluded_cotations = [
            'Acima 0.5',
            'Abaixo 2.5',
            'Abaixo 3.5',
            'Abaixo 4.5',
            'Abaixo 5.5',
            'Abaixo 3.0',
            'Abaixo 4.0',
            'Abaixo 5.0',
        ]

        if cotation_name in excluded_cotations:
            is_excluded = True


    #elif kind.pk == 63:
    #    is_excluded = True

    return is_excluded
