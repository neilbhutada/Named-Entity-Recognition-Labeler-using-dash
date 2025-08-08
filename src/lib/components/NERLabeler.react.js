/**
 * NERLabeler React Component
 * 
 * A React component for Named Entity Recognition (NER) text labeling.
 * Allows users to select text and assign entity labels interactively.
 * 
 * Features:
 * - Interactive text selection with mouse
 * - Popup label selection modal
 * - Entity highlighting and management
 * - Remove entities functionality
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
            modalPosition: { x: 0, y: 0 }
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
        const newEntity = {
            text: selectedText,
            label: labelType,
            start: selectedRange.startOffset,
            end: selectedRange.endOffset,
            id: Date.now() + Math.random()
        };

        const updatedEntities = [...(this.props.entities || []), newEntity];
        
        if (this.props.setProps) {
            this.props.setProps({ entities: updatedEntities });
        }

        this.setState({ 
            showLabelModal: false,
            selectedText: '',
            selectedRange: null
        });

        window.getSelection().removeAllRanges();
    }

    removeEntity = (entityId) => {
        const updatedEntities = this.props.entities.filter(entity => entity.id !== entityId);
        if (this.props.setProps) {
            this.props.setProps({ entities: updatedEntities });
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
                    title={`${entity.label}: ${entity.text}`}
                    onClick={(e) => {
                        e.stopPropagation();
                        if (window.confirm(`Remove "${entity.text}" (${entity.label})?`)) {
                            this.removeEntity(entity.id);
                        }
                    }}
                >
                    {entity.text}
                    <span className="ner-label-badge">{entity.label}</span>
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

    render() {
        const { labelTypes = ['PERSON', 'ORGANIZATION', 'LOCATION', 'MISCELLANEOUS'] } = this.props;
        const { showLabelModal, modalPosition } = this.state;

        return (
            <div className="ner-labeler-container">
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
        end: PropTypes.number.isRequired
    })),
    labelTypes: PropTypes.arrayOf(PropTypes.string),
    setProps: PropTypes.func
};

NERLabeler.defaultProps = {
    entities: [],
    labelTypes: ['PERSON', 'ORGANIZATION', 'LOCATION', 'MISCELLANEOUS']
};

export default NERLabeler;