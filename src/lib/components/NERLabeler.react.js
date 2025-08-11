/**
 * NERLabeler React Component
 * 
 * A React component for Named Entity Recognition (NER) text labeling with multi-user support.
 * Allows multiple users to select text and assign entity labels interactively.
 * 
 * Features:
 * - Interactive text selection with mouse
 * - Popup label selection modal
 * - Entity highlighting and management
 * - Remove entities functionality
 * - Multi-user annotation tracking with timestamps
 * - Annotation history with user attribution
 * - User information display
 * 
 * Author: Generated with Claude Code
 * License: MIT
 */

import React, { Component } from 'react';
import PropTypes from 'prop-types';
import './NERLabeler.css';

class NERLabeler extends Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedText: '',
            selectedRange: null,
            showLabelModal: false,
            modalPosition: { x: 0, y: 0 },
            showUserModal: false,
            tempUsername: ''
        };
        this.textRef = React.createRef();
    }

    componentDidMount() {
        document.addEventListener('mouseup', this.handleMouseUp);
        document.addEventListener('mousedown', this.handleMouseDown);
    }

    componentWillUnmount() {
        document.removeEventListener('mouseup', this.handleMouseUp);
        document.removeEventListener('mousedown', this.handleMouseDown);
    }

    handleMouseDown = (e) => {
        if (!this.textRef.current?.contains(e.target)) {
            this.setState({ showLabelModal: false });
        }
    }

    handleMouseUp = (e) => {
        if (!this.textRef.current?.contains(e.target)) return;

        const selection = window.getSelection();
        if (selection.rangeCount === 0 || selection.toString().trim() === '') {
            return;
        }

        const range = selection.getRangeAt(0);
        const selectedText = selection.toString().trim();
        
        if (selectedText.length === 0) return;

        // Calculate position for label modal
        const rect = range.getBoundingClientRect();
        const modalPosition = {
            x: rect.left + window.scrollX,
            y: rect.bottom + window.scrollY + 5
        };

        this.setState({
            selectedText,
            selectedRange: {
                startOffset: this.getAbsoluteOffset(range.startContainer, range.startOffset),
                endOffset: this.getAbsoluteOffset(range.endContainer, range.endOffset)
            },
            showLabelModal: true,
            modalPosition
        });
    }

    getAbsoluteOffset = (node, offset) => {
        let absoluteOffset = offset;
        let walker = document.createTreeWalker(
            this.textRef.current,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        let currentNode;
        while (currentNode = walker.nextNode()) {
            if (currentNode === node) {
                break;
            }
            absoluteOffset += currentNode.textContent.length;
        }
        return absoluteOffset;
    }

    handleLabelSelection = (labelType) => {
        const { selectedRange, selectedText } = this.state;
        const { currentUser } = this.props;
        
        if (!currentUser || !currentUser.id) {
            alert('Please set a username first!');
            return;
        }
        
        const timestamp = new Date().toISOString();
        const newEntity = {
            text: selectedText,
            label: labelType,
            start: selectedRange.startOffset,
            end: selectedRange.endOffset,
            id: Date.now() + Math.random(),
            user_id: currentUser.id,
            username: currentUser.name,
            timestamp: timestamp
        };

        const updatedEntities = [...(this.props.entities || []), newEntity];
        
        // Add to annotation history
        const historyEntry = {
            id: Date.now() + Math.random() + 0.1,
            action: 'add',
            entity: newEntity,
            user_id: currentUser.id,
            username: currentUser.name,
            timestamp: timestamp
        };
        
        const updatedHistory = [...(this.props.annotationHistory || []), historyEntry];
        
        if (this.props.setProps) {
            this.props.setProps({ 
                entities: updatedEntities,
                annotationHistory: updatedHistory
            });
        }

        this.setState({ 
            showLabelModal: false,
            selectedText: '',
            selectedRange: null
        });

        window.getSelection().removeAllRanges();
    }

    removeEntity = (entityId) => {
        const { currentUser, entities, annotationHistory } = this.props;
        
        if (!currentUser || !currentUser.id) {
            alert('Please set a username first!');
            return;
        }
        
        const entityToRemove = entities.find(entity => entity.id === entityId);
        const updatedEntities = entities.filter(entity => entity.id !== entityId);
        
        // Add to annotation history
        const historyEntry = {
            id: Date.now() + Math.random(),
            action: 'remove',
            entity: entityToRemove,
            user_id: currentUser.id,
            username: currentUser.name,
            timestamp: new Date().toISOString()
        };
        
        const updatedHistory = [...(annotationHistory || []), historyEntry];
        
        if (this.props.setProps) {
            this.props.setProps({ 
                entities: updatedEntities,
                annotationHistory: updatedHistory
            });
        }
    }

    renderHighlightedText = () => {
        const { text, entities = [] } = this.props;
        if (!text) return null;

        const sortedEntities = [...entities].sort((a, b) => a.start - b.start);
        let result = [];
        let lastIndex = 0;

        sortedEntities.forEach((entity, index) => {
            // Add text before entity
            if (entity.start > lastIndex) {
                result.push(
                    <span key={`text-${index}`}>
                        {text.slice(lastIndex, entity.start)}
                    </span>
                );
            }

            // Add highlighted entity
            result.push(
                <span
                    key={entity.id}
                    className={`ner-entity ner-${entity.label.toLowerCase()}`}
                    title={`${entity.label}: ${entity.text}\nAnnotated by: ${entity.username || 'Unknown'} at ${entity.timestamp ? new Date(entity.timestamp).toLocaleString() : 'Unknown time'}`}
                    onClick={(e) => {
                        e.stopPropagation();
                        if (window.confirm(`Remove "${entity.text}" (${entity.label})?`)) {
                            this.removeEntity(entity.id);
                        }
                    }}
                >
                    {entity.text}
                    <span className="ner-label-badge">{entity.label}</span>
                    {entity.username && (
                        <span className="ner-user-badge" title={`By ${entity.username} at ${entity.timestamp ? new Date(entity.timestamp).toLocaleString() : 'Unknown time'}`}>
                            @{entity.username}
                        </span>
                    )}
                </span>
            );

            lastIndex = entity.end;
        });

        // Add remaining text
        if (lastIndex < text.length) {
            result.push(
                <span key="text-end">
                    {text.slice(lastIndex)}
                </span>
            );
        }

        return result;
    }

    setUsername = (username) => {
        if (this.props.setProps) {
            this.props.setProps({
                currentUser: {
                    id: Date.now() + Math.random(),
                    name: username
                }
            });
        }
        this.setState({ showUserModal: false, tempUsername: '' });
    }

    renderUserInfo = () => {
        const { currentUser, showUserInfo = true } = this.props;
        
        if (!showUserInfo) return null;
        
        return (
            <div className="ner-user-info">
                <h4>Current User:</h4>
                {currentUser && currentUser.name ? (
                    <div className="ner-current-user">
                        <span className="ner-username">@{currentUser.name}</span>
                        <button 
                            className="ner-change-user-btn"
                            onClick={() => this.setState({ showUserModal: true, tempUsername: '' })}
                        >
                            Change User
                        </button>
                    </div>
                ) : (
                    <button 
                        className="ner-set-user-btn"
                        onClick={() => this.setState({ showUserModal: true, tempUsername: '' })}
                    >
                        Set Username
                    </button>
                )}
            </div>
        );
    }

    renderAnnotationHistory = () => {
        const { annotationHistory = [], showHistory = true } = this.props;
        
        if (!showHistory || annotationHistory.length === 0) return null;
        
        const sortedHistory = [...annotationHistory].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        return (
            <div className="ner-annotation-history">
                <h4>Annotation History ({annotationHistory.length} actions):</h4>
                <div className="ner-history-list">
                    {sortedHistory.slice(0, 10).map(entry => (
                        <div key={entry.id} className="ner-history-item">
                            <span className={`ner-action-badge ner-action-${entry.action}`}>
                                {entry.action === 'add' ? '+' : '×'}
                            </span>
                            <span className="ner-history-text">
                                <strong>@{entry.username}</strong> {entry.action === 'add' ? 'added' : 'removed'} 
                                <span className={`ner-entity-label ner-${entry.entity.label.toLowerCase()}`}>
                                    {entry.entity.label}
                                </span> 
                                "{entry.entity.text}"
                            </span>
                            <span className="ner-history-time">
                                {new Date(entry.timestamp).toLocaleString()}
                            </span>
                        </div>
                    ))}
                    {annotationHistory.length > 10 && (
                        <div className="ner-history-more">
                            ... and {annotationHistory.length - 10} more actions
                        </div>
                    )}
                </div>
            </div>
        );
    }

    render() {
        const { labelTypes = ['PERSON', 'ORGANIZATION', 'LOCATION', 'MISCELLANEOUS'] } = this.props;
        const { showLabelModal, modalPosition, showUserModal, tempUsername } = this.state;

        return (
            <div className="ner-labeler-container">
                {this.renderUserInfo()}
                <div 
                    ref={this.textRef}
                    className="ner-text-container"
                    style={{ userSelect: 'text' }}
                >
                    {this.renderHighlightedText()}
                </div>

                {showLabelModal && (
                    <div 
                        className="ner-label-modal"
                        style={{
                            position: 'absolute',
                            left: modalPosition.x,
                            top: modalPosition.y,
                            zIndex: 1000
                        }}
                    >
                        <div className="ner-modal-content">
                            <h4>Select Label Type:</h4>
                            {labelTypes.map(labelType => (
                                <button
                                    key={labelType}
                                    className={`ner-label-btn ner-${labelType.toLowerCase()}`}
                                    onClick={() => this.handleLabelSelection(labelType)}
                                >
                                    {labelType}
                                </button>
                            ))}
                            <button 
                                className="ner-cancel-btn"
                                onClick={() => this.setState({ showLabelModal: false })}
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )}

                {showUserModal && (
                    <div className="ner-user-modal-overlay">
                        <div className="ner-user-modal">
                            <h4>Set Username</h4>
                            <input
                                type="text"
                                placeholder="Enter your username"
                                value={tempUsername}
                                onChange={(e) => this.setState({ tempUsername: e.target.value })}
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter' && tempUsername.trim()) {
                                        this.setUsername(tempUsername.trim());
                                    }
                                }}
                                autoFocus
                            />
                            <div className="ner-user-modal-buttons">
                                <button 
                                    onClick={() => tempUsername.trim() && this.setUsername(tempUsername.trim())}
                                    disabled={!tempUsername.trim()}
                                >
                                    Set
                                </button>
                                <button onClick={() => this.setState({ showUserModal: false, tempUsername: '' })}>
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {this.props.entities && this.props.entities.length > 0 && (
                    <div className="ner-entities-summary">
                        <h4>Labeled Entities ({this.props.entities.length}):</h4>
                        <div className="ner-entities-list">
                            {this.props.entities.map(entity => (
                                <div key={entity.id} className="ner-entity-item">
                                    <span className={`ner-entity-label ner-${entity.label.toLowerCase()}`}>
                                        {entity.label}
                                    </span>
                                    <span className="ner-entity-text">{entity.text}</span>
                                    {entity.username && (
                                        <span className="ner-entity-user">by @{entity.username}</span>
                                    )}
                                    <button 
                                        className="ner-remove-btn"
                                        onClick={() => this.removeEntity(entity.id)}
                                    >
                                        ×
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
                
                {this.renderAnnotationHistory()}
            </div>
        );
    }
}

NERLabeler.propTypes = {
    id: PropTypes.string,
    text: PropTypes.string.isRequired,
    entities: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
        text: PropTypes.string.isRequired,
        label: PropTypes.string.isRequired,
        start: PropTypes.number.isRequired,
        end: PropTypes.number.isRequired,
        user_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        username: PropTypes.string,
        timestamp: PropTypes.string
    })),
    labelTypes: PropTypes.arrayOf(PropTypes.string),
    currentUser: PropTypes.shape({
        id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        name: PropTypes.string
    }),
    annotationHistory: PropTypes.arrayOf(PropTypes.shape({
        id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
        action: PropTypes.oneOf(['add', 'remove']).isRequired,
        entity: PropTypes.object.isRequired,
        user_id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
        username: PropTypes.string,
        timestamp: PropTypes.string
    })),
    showUserInfo: PropTypes.bool,
    showHistory: PropTypes.bool,
    setProps: PropTypes.func
};

NERLabeler.defaultProps = {
    entities: [],
    labelTypes: ['PERSON', 'ORGANIZATION', 'LOCATION', 'MISCELLANEOUS'],
    annotationHistory: [],
    showUserInfo: true,
    showHistory: true
};

export default NERLabeler;