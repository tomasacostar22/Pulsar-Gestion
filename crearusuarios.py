import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from usuarios.models import Usuario                                                                                                                                                                               
                                                                                                                                                                                                                    
usuarios = [                                                                                                                                                                                                      
      ('tomas.acosta', 'Tomas', 'Acosta', 'tomasacostar22@gmail.com')                                                                                                             
  ]                                                                                                                                                                                                                 
                                                                                                                                                                                                                    
for username, first_name, last_name, email in usuarios:                                                                                                                                                           
      u = Usuario.objects.create_user(                                                                                                                                                                              
          username=username,                                                                                                                                                                                        
          email=email,                                                                                                                                                                                              
          password='pulsar',                                                                                                                                                                                        
          first_name=first_name,                                                                                                                                                                                    
          last_name=last_name,                                                                                                                                                                                      
      )                                                                                                                                                                                                             
      print(f'Creado: {u.username} - {u.email}')                                                                                                                                                                    
                                                                                                                                                                                                                    
print(f'\nTotal: {len(usuarios)} usuarios creados')                                                                                                                                                                                                                                                       