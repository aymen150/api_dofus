def traitement_image_map(image) : 
    data = np.array(image)   # "data" is a height x width x 4 numpy array
    red, green, blue  = data.T # Temporarily unpack the bands for readability
    ecriture_noir = ((red < v.color_pos_dofus_p[0]) & (red > v.color_pos_dofus_m[0])) & ((green < v.color_pos_dofus_p[1] ) & (green > v.color_pos_dofus_m[1] )) & ((blue < v.color_pos_dofus_p[2] ) &  (blue > v.color_pos_dofus_m[2] ))
    fond_blanc = (ecriture_noir == False)
    data[..., :][fond_blanc.T] = (255,255,255) # Transpose back needed
    data[..., :][ecriture_noir.T] = (0,0,0) # Transpose back needed
    return Image.fromarray(data)


def traitement_image_bouton_pret(image) :
    data = np.array(image)   # "data" is a height x width x 4 numpy array
    red, green, blue  = data.T # Temporarily unpack the bands for readability
    ecriture_noir = ((red < v.color_bouton_pret[0] + 50)  & (green < v.color_bouton_pret[1] + 50) & (blue < v.color_bouton_pret[2] + 50))
    fond_blanc = (ecriture_noir == False)
    data[..., :][fond_blanc.T] = (255,255,255) # Transpose back needed
    data[..., :][ecriture_noir.T] = (0,0,0) # Transpose back needed
    return Image.fromarray(data)

def traitement_image_PA_PM(image) :
    data = np.array(image) 
    red, green, blue = data.T 
    areas_PA = ( red > v.color_PA_PM[0] - 100 ) & (green > v.color_PA_PM[0] - 100 ) & (blue > v.color_PA_PM[0] - 100) 
    areas_background = (areas_PA == False) 
    data[..., :][areas_background.T] = (255,255,255) # Transpose back needed
    data[..., :][areas_PA.T] = (0,0,0)
    return Image.fromarray(data)


