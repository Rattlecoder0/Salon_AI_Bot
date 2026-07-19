from repository.settings_repository import update_setting
# from sync.settings_sync import sync_setting


# Update Salon Setting
def update_salon_setting(key, value):

    if update_setting(key, value):

        # sync_setting(key, value)

        return True

    return False

# Update buffer time
def update_buffer_time(buffer_minutes):

    return update_salon_setting("BUFFER_MINUTES", str(buffer_minutes))

# Update open time
def update_open_time(open_time):

    return update_salon_setting("OPEN_TIME", open_time)

# Update close time
def update_close_time(close_time):

    return update_salon_setting("CLOSE_TIME", close_time)