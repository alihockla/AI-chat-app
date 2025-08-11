
def test_save_and_load_messages(memory_db):
    client_id = "client1"
    memory_db.save_message(client_id, "user", "Hello")
    memory_db.save_message(client_id, "ai", "Hi there")
    history = memory_db.load_history(client_id)

    assert len(history) == 2
    assert history[0] == ("user", "Hello")
    assert history[1] == ("ai", "Hi there")


def test_last_response_id(memory_db):
    client_id = "client1"
    assert memory_db.get_last_response_id(client_id) is None

    memory_db.save_last_response_id(client_id, "resp123")
    assert memory_db.get_last_response_id(client_id) == "resp123"
