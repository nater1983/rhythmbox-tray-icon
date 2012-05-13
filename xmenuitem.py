"""
            menu = (Menu)interface_action_service.UIManager.GetWidget("/NotificationAreaIconMenu");
            menu.Show ();
To add to the menu
                    rating_menu_item = new RatingMenuItem ();
                    rating_menu_item.Activated += OnRatingChanged;
                    ToggleRatingMenuSensitive ();
                    menu.Insert (rating_menu_item, i + 2);
"""

# Custom widget
# http://www.pygtk.org/articles/writing-a-custom-widget-using-pygtk/writing-a-custom-widget-using-pygtk.htm

#RatingMenuItem.cs
# http://www.koders.com/csharp/fidDD780B47D5B33FDC09A53DA087F1D8DEDE63EA52.aspx?s=combobox

# ComplexMenuItem.cs
# http://www.koders.com/csharp/fidF4D19E25855532926F790139B60623C08A6D2123.aspx?s=combobox

