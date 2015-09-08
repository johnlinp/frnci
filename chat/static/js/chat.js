(function() {
	var updateFriendItem = function(friendId, words) {
		$('.friend-item').each(function() {
			if ($(this).attr('user-id') == friendId) {
				$(this).find('.words').html(words);
				return false;
			}
		});
	};

	var registerWebSocket = function() {
		swampdragon.open(function() {
			swampdragon.subscribe('sentence', 'local-channel', {source: 'from-me'});
			swampdragon.subscribe('sentence', 'local-channel', {source: 'to-me'});
			swampdragon.onChannelMessage(function(channels, message) {
				var friendId = getActiveFriendId();
				updateFriendItem(friendId, message.data.words);
				if (message.data.recipient == friendId || message.data.sender == friendId) {
					renderSentence(message.data.sender_name, message.data.words);
					scrollConversationToBottom();
				}
			});
		});
	};

	var registerTyping = function() {
		$('#typing').keydown(function(evt) {
			if (evt.which != 13) { // enter key
				return;
			}

			var words = $('#typing').html();
			$('#typing').html('');

			var friendId = getActiveFriendId();

			swampdragon.create('sentence', {words: words, recipient_id: friendId});
		});
	};

	var renderSentence = function(sentenceName, sentenceWords) {
		var $sentenceItem = $('<div/>');
		var $sentenceName = $('<div/>');
		var $sentenceWords = $('<div/>');

		$sentenceItem.addClass('sentence');
		$sentenceName.addClass('name');
		$sentenceWords.addClass('words');

		$sentenceName.html(sentenceName);
		$sentenceWords.html(sentenceWords);

		$sentenceItem.append($sentenceName);
		$sentenceItem.append($sentenceWords);

		$('#conversation').append($sentenceItem);
	};

	var scrollConversationToBottom = function() {
		$('#conversation').scrollTop($('#conversation')[0].scrollHeight);
	};

	var renderConversation = function(conversation) {
		for (var idx = 0; idx < conversation.length; ++idx) {
			var sentence = conversation[idx];
			renderSentence(sentence.name, sentence.words);
		}
		scrollConversationToBottom();
	};

	var getActiveFriendId = function() {
		return $('.friend-item.active').attr('user-id');
	};

	var loadFriendConversation = function() {
		var activeFriendId = getActiveFriendId();

		$('#conversation').empty();
		$.get('/chat/conversation/', {friend_id: activeFriendId}, function(response) {
			if (!response.success) {
				console.log('load chat conversation failed: ' + response.message);
				return;
			}

			renderConversation(response.data);

			$('#typing').focus();
		}, 'json');
	};

	var registerClickFriendItem = function($friendItem) {
		$friendItem.click(function() {
			$('.friend-item').removeClass('active');
			$friendItem.addClass('active');

			loadFriendConversation();
		});
	};

	var renderFriendList = function(friendList) {
		for (var idx = 0; idx < friendList.length; ++idx) {
			var friendItem = friendList[idx];

			var $friendItem = $('<div/>');
			var $friendName = $('<div/>');
			var $friendWords = $('<div/>');

			$friendItem.addClass('friend-item');
			$friendName.addClass('name');
			$friendWords.addClass('words');
			if (idx == 0) {
				$friendItem.addClass('active');
			}

			$friendName.html(friendItem.name);
			$friendWords.html(friendItem.latest_words);

			$friendItem.append($friendName);
			$friendItem.append($friendWords);

			$friendItem.attr('user-id', friendItem.user_id);

			registerClickFriendItem($friendItem);

			$('#friend-list').append($friendItem);
		}
	};

	var loadFriendList = function() {
		$.get('/chat/friend-list/', function(response) {
			if (!response.success) {
				console.log('load chat friend list failed: ' + response.message);
				return;
			}

			renderFriendList(response.data);

			loadFriendConversation();
		}, 'json');
	};

	loadFriendList();
	registerWebSocket();
	registerTyping();
})();
